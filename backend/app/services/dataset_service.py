import pandas as pd
from ..extensions import db
from ..models import DataQualityReport

class DatasetService:
    """Service for dataset operations"""
    
    def generate_quality_report(self, df, dataset_id=None, dataset_version_id=None):
        """Generate a data quality report for a dataframe"""
        missing_count = df.isnull().sum().sum()
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        
        # Check for invalid coordinates if latitude/longitude exist
        invalid_coordinate_count = 0
        if 'latitude' in df.columns and 'longitude' in df.columns:
            invalid_lat = ~df['latitude'].between(-90, 90)
            invalid_lon = ~df['longitude'].between(-180, 180)
            invalid_coordinate_count = (invalid_lat | invalid_lon).sum()
        
        validation_summary = {
            'columns': list(df.columns),
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_by_column': df.isnull().sum().to_dict(),
            'duplicate_rows': int(duplicate_count),
            'invalid_coordinates': int(invalid_coordinate_count),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        report = DataQualityReport(
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            missing_value_count=int(missing_count),
            duplicate_count=int(duplicate_count),
            invalid_coordinate_count=int(invalid_coordinate_count),
            validation_summary=validation_summary
        )
        
        db.session.add(report)
        db.session.commit()
        
        return report
    
    def validate_schema(self, df, expected_columns=None):
        """Validate dataframe schema"""
        issues = []
        
        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
        
        return issues
