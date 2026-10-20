"""
Seed the database with demonstration data.
This creates a synthetic dataset for testing and demonstration purposes.
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    Dataset, DatasetVersion, DataQualityReport,
    ReferenceSite, DataSource
)

def seed_demo_data():
    """Seed the database with demonstration data"""
    app = create_app('development')
    
    with app.app_context():
        print("Seeding demonstration data...")
        
        # Create data source
        source = DataSource(
            name='Demo Satellite Data',
            provider='Synthetic Demo',
            source_url='https://demo.example.com',
            license='MIT',
            description='Synthetic demonstration dataset for space archaeology platform'
        )
        db.session.add(source)
        db.session.commit()
        
        # Generate synthetic archaeological observation data
        np.random.seed(42)
        n_records = 500
        
        # Generate realistic-looking coordinates (Mediterranean region)
        base_lat = 37.0
        base_lon = 25.0
        latitudes = np.random.normal(base_lat, 2.0, n_records)
        longitudes = np.random.normal(base_lon, 2.0, n_records)
        
        # Generate satellite indices
        ndvi = np.random.beta(2, 2, n_records)  # Vegetation index (0-1)
        ndbi = np.random.normal(0, 0.3, n_records)  # Built-up index
        elevation = np.random.normal(200, 150, n_records)  # Elevation in meters
        soil_moisture = np.random.beta(1.5, 2, n_records)  # Soil moisture (0-1)
        surface_temperature = np.random.normal(25, 5, n_records)  # Temperature in Celsius
        distance_from_water = np.random.exponential(5, n_records)  # Distance to water in km
        
        # Generate dates over past year
        base_date = datetime.now() - timedelta(days=365)
        observation_dates = [base_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_records)]
        
        # Generate site types and archaeological status
        site_types = np.random.choice(['settlement', 'burial', 'fortification', 'ceremonial', 'unknown'], n_records)
        archaeological_statuses = np.random.choice(['verified', 'candidate', 'unverified', None], n_records, p=[0.1, 0.2, 0.3, 0.4])
        
        # Create dataframe
        df = pd.DataFrame({
            'record_id': [f"REC_{i:06d}" for i in range(n_records)],
            'site_id': [f"SITE_{i:04d}" if np.random.random() > 0.5 else None for i in range(n_records)],
            'latitude': latitudes,
            'longitude': longitudes,
            'elevation': elevation,
            'ndvi': ndvi,
            'ndbi': ndbi,
            'soil_moisture': soil_moisture,
            'surface_temperature': surface_temperature,
            'distance_from_water': distance_from_water,
            'region': np.random.choice(['Aegean', 'Anatolia', 'Levant', 'Egypt', 'Mesopotamia'], n_records),
            'observation_date': observation_dates,
            'sensor_name': np.random.choice(['Landsat-8', 'Sentinel-2', 'MODIS'], n_records),
            'site_type': site_types,
            'archaeological_status': archaeological_statuses,
            'source_url': 'https://demo.example.com'
        })
        
        # Save to CSV
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample')
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, 'demo_satellite_data.csv')
        df.to_csv(csv_path, index=False)
        
        # Create dataset record
        dataset = Dataset(
            name='Demo Satellite Archaeological Data',
            description='Synthetic demonstration dataset with satellite observations and archaeological site information',
            source_type='csv',
            source_url='https://demo.example.com',
            file_path=csv_path,
            storage_key='demo_satellite_data.csv',
            schema_json={
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'row_count': len(df),
                'column_count': len(df.columns)
            },
            record_count=len(df),
            provenance='Synthetic demonstration data generated for testing'
        )
        db.session.add(dataset)
        db.session.commit()
        
        # Create initial version
        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            file_path=csv_path,
            record_count=len(df),
            transformation_summary={'type': 'initial_import', 'source': 'synthetic_generation'}
        )
        db.session.add(version)
        db.session.commit()
        
        # Generate quality report
        from app.services.dataset_service import DatasetService
        service = DatasetService()
        service.generate_quality_report(df, dataset.id, version.id)
        
        # Create reference sites
        reference_sites = [
            ReferenceSite(
                site_name='Troy',
                latitude=39.9576,
                longitude=26.2389,
                region='Anatolia',
                site_type='settlement',
                source_url='https://en.wikipedia.org/wiki/Troy',
                verification_status='verified'
            ),
            ReferenceSite(
                site_name='Knossos',
                latitude=35.2990,
                longitude=25.1611,
                region='Aegean',
                site_type='settlement',
                source_url='https://en.wikipedia.org/wiki/Knossos',
                verification_status='verified'
            ),
            ReferenceSite(
                site_name='Pyramids of Giza',
                latitude=29.9792,
                longitude=31.1342,
                region='Egypt',
                site_type='burial',
                source_url='https://en.wikipedia.org/wiki/Giza_pyramid_complex',
                verification_status='verified'
            ),
            ReferenceSite(
                site_name='Petra',
                latitude=30.3285,
                longitude=35.4444,
                region='Levant',
                site_type='settlement',
                source_url='https://en.wikipedia.org/wiki/Petra',
                verification_status='verified'
            ),
            ReferenceSite(
                site_name='Ur',
                latitude=30.9625,
                longitude=46.1036,
                region='Mesopotamia',
                site_type='settlement',
                source_url='https://en.wikipedia.org/wiki/Ur',
                verification_status='verified'
            )
        ]
        
        for site in reference_sites:
            db.session.add(site)
        
        db.session.commit()
        
        print(f"\nDemo data seeded successfully:")
        print(f"  - Dataset: {dataset.name} ({dataset.record_count} records)")
        print(f"  - Dataset version: {version.version_number}")
        print(f"  - Reference sites: {len(reference_sites)}")
        print(f"  - CSV file: {csv_path}")
        print("\nNote: This is synthetic demonstration data for testing purposes only.")
        print("For real archaeological analysis, import actual satellite and archaeological datasets.")

if __name__ == '__main__':
    seed_demo_data()
