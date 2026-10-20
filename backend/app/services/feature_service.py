import pandas as pd
import numpy as np
import os
import uuid
from datetime import datetime
from ..extensions import db
from ..models import DatasetVersion, Dataset
from .preprocessing_service import PreprocessingService

class FeatureService:
    """Service for feature engineering operations"""
    
    def get_available_features(self):
        """Get list of available feature engineering options"""
        return {
            'numerical_features': [
                {
                    'name': 'ndvi_anomaly',
                    'description': 'NDVI anomaly relative to reference period',
                    'required_columns': ['ndvi'],
                    'parameters': ['reference_mean', 'reference_std']
                },
                {
                    'name': 'elevation_category',
                    'description': 'Categorize elevation into ranges',
                    'required_columns': ['elevation'],
                    'parameters': ['bins']
                },
                {
                    'name': 'vegetation_category',
                    'description': 'Categorize NDVI into vegetation classes',
                    'required_columns': ['ndvi'],
                    'parameters': ['thresholds']
                },
                {
                    'name': 'spectral_anomaly_score',
                    'description': 'Calculate spectral anomaly from multiple indices',
                    'required_columns': ['ndvi', 'ndbi'],
                    'parameters': []
                }
            ],
            'spatial_features': [
                {
                    'name': 'distance_to_water',
                    'description': 'Distance to nearest water source (requires water data)',
                    'required_columns': ['latitude', 'longitude'],
                    'parameters': ['water_sources']
                },
                {
                    'name': 'local_site_density',
                    'description': 'Density of sites within radius',
                    'required_columns': ['latitude', 'longitude'],
                    'parameters': ['radius_km']
                }
            ],
            'temporal_features': [
                {
                    'name': 'temporal_change_score',
                    'description': 'Change in values over time',
                    'required_columns': ['observation_date', 'ndvi'],
                    'parameters': []
                }
            ]
        }
    
    def preview_features(self, dataset_version_id, feature_config):
        """Preview feature engineering without saving"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        original_cols = list(df.columns)
        enhanced_df = self._apply_features(df, feature_config)
        
        return {
            'original_columns': original_cols,
            'new_columns': [c for c in enhanced_df.columns if c not in original_cols],
            'preview_sample': enhanced_df.head(5).to_dict(orient='records'),
            'feature_count': len(enhanced_df.columns) - len(original_cols)
        }
    
    def generate_features(self, dataset_version_id, feature_config):
        """Generate features and create new dataset version"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        # Apply features
        enhanced_df = self._apply_features(df, feature_config)
        
        # Get parent dataset
        dataset = Dataset.query.get(version.dataset_id)
        
        # Determine new version number
        max_version = db.session.query(db.func.max(DatasetVersion.version_number)).filter_by(
            dataset_id=dataset.id
        ).scalar() or 0
        new_version_number = max_version + 1
        
        # Save enhanced data
        unique_filename = f"{uuid.uuid4().hex}_features_v{new_version_number}.csv"
        file_path = version.file_path.replace('.csv', f'_features_v{new_version_number}.csv')
        enhanced_df.to_csv(file_path, index=False)
        
        # Create new version
        new_version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=new_version_number,
            parent_version_id=dataset_version_id,
            transformation_summary={'type': 'feature_engineering', 'features': feature_config},
            file_path=file_path,
            record_count=len(enhanced_df)
        )
        db.session.add(new_version)
        db.session.commit()
        
        return {
            'version': new_version.to_dict(),
            'new_columns': [c for c in enhanced_df.columns if c not in df.columns]
        }
    
    def _load_dataframe(self, file_path):
        """Load dataframe from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            return pd.read_json(file_path)
    
    def _apply_features(self, df, feature_config):
        """Apply feature engineering based on configuration"""
        result = df.copy()
        
        for feature in feature_config:
            feature_name = feature.get('name')
            params = feature.get('parameters', {})
            
            if feature_name == 'ndvi_anomaly' and 'ndvi' in result.columns:
                ref_mean = params.get('reference_mean', result['ndvi'].mean())
                ref_std = params.get('reference_std', result['ndvi'].std())
                result['ndvi_anomaly'] = (result['ndvi'] - ref_mean) / ref_std if ref_std > 0 else 0
            
            elif feature_name == 'elevation_category' and 'elevation' in result.columns:
                bins = params.get('bins', [0, 500, 1000, 1500, 2000, float('inf')])
                labels = ['very_low', 'low', 'medium', 'high', 'very_high']
                result['elevation_category'] = pd.cut(result['elevation'], bins=bins, labels=labels)
            
            elif feature_name == 'vegetation_category' and 'ndvi' in result.columns:
                thresholds = params.get('thresholds', [0.1, 0.3, 0.5, 0.7])
                result['vegetation_category'] = pd.cut(
                    result['ndvi'],
                    bins=[-float('inf')] + thresholds + [float('inf')],
                    labels=['bare', 'sparse', 'moderate', 'dense', 'very_dense']
                )
            
            elif feature_name == 'spectral_anomaly_score' and 'ndvi' in result.columns and 'ndbi' in result.columns:
                result['spectral_anomaly_score'] = np.sqrt(result['ndvi']**2 + result['ndbi']**2)
            
            elif feature_name == 'local_site_density' and 'latitude' in result.columns and 'longitude' in result.columns:
                radius_km = params.get('radius_km', 10)
                # Simplified density calculation
                result['local_site_density'] = self._calculate_density(result, radius_km)
        
        return result
    
    def _calculate_density(self, df, radius_km):
        """Calculate local site density (simplified)"""
        # This is a simplified version - in production, use spatial indexing
        densities = []
        for idx, row in df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            # Count points within radius (approximate)
            lat_diff = (df['latitude'] - lat).abs()
            lon_diff = (df['longitude'] - lon).abs()
            # Rough approximation: 1 degree ~ 111km
            count = ((lat_diff * 111 <= radius_km) & (lon_diff * 111 <= radius_km)).sum()
            densities.append(count - 1)  # Exclude self
        return densities
