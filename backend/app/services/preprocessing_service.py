import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import os
from datetime import datetime
from ..extensions import db
from ..models import DatasetVersion, Dataset, DataQualityReport

class PreprocessingService:
    """Service for data preprocessing operations"""
    
    def preview_transformations(self, dataset_version_id, configuration):
        """Preview preprocessing transformations without saving"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        original_df = df.copy()
        transformed_df = self._apply_transformations(df, configuration)
        
        return {
            'original_rows': len(original_df),
            'transformed_rows': len(transformed_df),
            'original_columns': list(original_df.columns),
            'transformed_columns': list(transformed_df.columns),
            'preview_sample': transformed_df.head(5).to_dict(orient='records'),
            'transformation_summary': self._generate_summary(original_df, transformed_df, configuration)
        }
    
    def run_preprocessing(self, dataset_version_id, configuration, job_id):
        """Run preprocessing and create new dataset version"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        # Apply transformations
        transformed_df = self._apply_transformations(df, configuration)
        
        # Get parent dataset
        dataset = Dataset.query.get(version.dataset_id)
        
        # Determine new version number
        max_version = db.session.query(db.func.max(DatasetVersion.version_number)).filter_by(
            dataset_id=dataset.id
        ).scalar() or 0
        new_version_number = max_version + 1
        
        # Save transformed data
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_v{new_version_number}.csv"
        file_path = version.file_path.replace('.csv', f'_v{new_version_number}.csv')
        transformed_df.to_csv(file_path, index=False)
        
        # Create new version
        new_version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=new_version_number,
            parent_version_id=dataset_version_id,
            transformation_summary=configuration,
            file_path=file_path,
            record_count=len(transformed_df)
        )
        db.session.add(new_version)
        db.session.commit()
        
        # Generate quality report for new version
        service = __import__('dataset_service', fromlist=['DatasetService']).DatasetService()
        service.generate_quality_report(transformed_df, dataset.id, new_version.id)
        
        return new_version
    
    def _load_dataframe(self, file_path):
        """Load dataframe from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            return pd.read_json(file_path)
    
    def _apply_transformations(self, df, configuration):
        """Apply transformations based on configuration"""
        result = df.copy()
        
        # Handle missing values
        if configuration.get('handle_missing'):
            strategy = configuration.get('missing_strategy', 'drop')
            columns = configuration.get('missing_columns', [])
            
            if strategy == 'drop' and configuration.get('drop_missing_rows'):
                result = result.dropna(subset=columns if columns else None)
            elif strategy == 'mean':
                for col in columns if columns else result.select_dtypes(include=[np.number]).columns:
                    if col in result.columns and result[col].isnull().any():
                        result[col].fillna(result[col].mean(), inplace=True)
            elif strategy == 'median':
                for col in columns if columns else result.select_dtypes(include=[np.number]).columns:
                    if col in result.columns and result[col].isnull().any():
                        result[col].fillna(result[col].median(), inplace=True)
            elif strategy == 'mode':
                for col in columns if columns else result.columns:
                    if col in result.columns and result[col].isnull().any():
                        result[col].fillna(result[col].mode()[0], inplace=True)
        
        # Remove duplicates
        if configuration.get('remove_duplicates'):
            result = result.drop_duplicates()
        
        # Drop columns
        if configuration.get('drop_columns'):
            result = result.drop(columns=configuration['drop_columns'], errors='ignore')
        
        # Rename columns
        if configuration.get('rename_columns'):
            result = result.rename(columns=configuration['rename_columns'])
        
        # Filter invalid coordinates
        if configuration.get('filter_invalid_coordinates'):
            if 'latitude' in result.columns and 'longitude' in result.columns:
                result = result[
                    (result['latitude'].between(-90, 90)) &
                    (result['longitude'].between(-180, 180))
                ]
        
        # Scale numerical features
        if configuration.get('scale_features'):
            scaler_type = configuration.get('scaler', 'standard')
            columns = configuration.get('scale_columns', [])
            
            numeric_cols = columns if columns else result.select_dtypes(include=[np.number]).columns
            if scaler_type == 'standard':
                scaler = StandardScaler()
            elif scaler_type == 'minmax':
                scaler = MinMaxScaler()
            else:
                scaler = StandardScaler()
            
            for col in numeric_cols:
                if col in result.columns:
                    result[col] = scaler.fit_transform(result[[col]])
        
        # Encode categorical variables
        if configuration.get('encode_categorical'):
            columns = configuration.get('encode_columns', [])
            cat_cols = columns if columns else result.select_dtypes(include=['object']).columns
            
            for col in cat_cols:
                if col in result.columns:
                    le = LabelEncoder()
                    result[col] = le.fit_transform(result[col].astype(str))
        
        return result
    
    def _generate_summary(self, original_df, transformed_df, configuration):
        """Generate transformation summary"""
        return {
            'configuration': configuration,
            'rows_removed': len(original_df) - len(transformed_df),
            'columns_added': len(transformed_df.columns) - len(original_df.columns),
            'columns_removed': len(original_df.columns) - len(transformed_df.columns),
            'timestamp': datetime.utcnow().isoformat()
        }
