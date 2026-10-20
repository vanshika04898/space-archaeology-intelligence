import pandas as pd
from datetime import datetime
from ..extensions import db
from ..models import (
    ETLJob, Dataset, DatasetVersion,
    FactObservation, DimDate, DimLocation, DimSatellite, DimSite, DimSource
)
from sqlalchemy import func, desc

class WarehouseService:
    """Service for data warehouse operations"""
    
    def get_schema(self):
        """Get warehouse schema information"""
        return {
            'fact_table': {
                'name': 'fact_observation',
                'columns': [
                    'observation_key', 'date_key', 'location_key', 'satellite_key',
                    'site_key', 'source_key', 'ndvi', 'ndbi', 'elevation',
                    'soil_moisture', 'surface_temperature', 'distance_from_water',
                    'quality_flag', 'observation_count'
                ]
            },
            'dimension_tables': {
                'dim_date': ['date_key', 'full_date', 'day', 'month', 'quarter', 'year', 'season'],
                'dim_location': ['location_key', 'latitude', 'longitude', 'region', 'country'],
                'dim_satellite': ['satellite_key', 'satellite_name', 'sensor_name', 'spatial_resolution', 'source_identifier'],
                'dim_site': ['site_key', 'site_identifier', 'site_type', 'historical_period', 'verification_status'],
                'dim_source': ['source_key', 'provider', 'source_url', 'license', 'retrieval_date']
            }
        }
    
    def get_summary(self):
        """Get warehouse summary statistics"""
        return {
            'fact_observations': db.session.query(func.count(FactObservation.observation_key)).scalar() or 0,
            'dim_dates': db.session.query(DimDate).count(),
            'dim_locations': db.session.query(DimLocation).count(),
            'dim_satellites': db.session.query(DimSatellite).count(),
            'dim_sites': db.session.query(DimSite).count(),
            'dim_sources': db.session.query(DimSource).count(),
            'last_etl': db.session.query(ETLJob).order_by(desc(ETLJob.started_at)).first()
        }
    
    def run_etl(self, source_dataset_id, job_type='full_load'):
        """Run ETL job to load data into warehouse"""
        # Create ETL job record
        job = ETLJob(
            source_dataset_id=source_dataset_id,
            job_type=job_type,
            status='running'
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            # Get source dataset
            dataset = Dataset.query.get(source_dataset_id)
            if not dataset:
                raise ValueError("Source dataset not found")
            
            # Load source data
            version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
            if not version:
                raise ValueError("No dataset version found")
            
            df = self._load_dataframe(version.file_path)
            
            job.rows_read = len(df)
            
            # Transform and load dimensions first
            rows_inserted = 0
            rows_rejected = 0
            
            # Load date dimension
            if 'observation_date' in df.columns:
                df['observation_date'] = pd.to_datetime(df['observation_date'])
                dates_loaded = self._load_date_dimension(df['observation_date'])
                rows_inserted += dates_loaded
            
            # Load location dimension
            if 'latitude' in df.columns and 'longitude' in df.columns:
                locations_loaded = self._load_location_dimension(df[['latitude', 'longitude', 'region']])
                rows_inserted += locations_loaded
            
            # Load satellite dimension
            if 'sensor_name' in df.columns:
                satellites_loaded = self._load_satellite_dimension(df[['sensor_name']])
                rows_inserted += satellites_loaded
            
            # Load source dimension
            sources_loaded = self._load_source_dimension(dataset)
            rows_inserted += sources_loaded
            
            # Load fact table
            facts_loaded = self._load_fact_table(df, job.id)
            rows_inserted += facts_loaded
            
            job.rows_inserted = rows_inserted
            job.rows_rejected = rows_rejected
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'job_id': job.id,
                'status': 'completed',
                'rows_read': job.rows_read,
                'rows_inserted': job.rows_inserted,
                'rows_rejected': job.rows_rejected
            }
            
        except Exception as e:
            job.status = 'failed'
            job.error_summary = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            raise e
    
    def _load_dataframe(self, file_path):
        """Load dataframe from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            return pd.read_json(file_path)
    
    def _load_date_dimension(self, dates):
        """Load date dimension"""
        count = 0
        for date in dates.dropna().unique():
            date_key = int(date.strftime('%Y%m%d'))
            if not DimDate.query.get(date_key):
                dim_date = DimDate(
                    date_key=date_key,
                    full_date=date.date(),
                    day=date.day,
                    month=date.month,
                    quarter=(date.month - 1) // 3 + 1,
                    year=date.year,
                    season='spring' if date.month in [3,4,5] else 'summer' if date.month in [6,7,8] else 'fall' if date.month in [9,10,11] else 'winter'
                )
                db.session.add(dim_date)
                count += 1
        db.session.commit()
        return count
    
    def _load_location_dimension(self, location_data):
        """Load location dimension"""
        count = 0
        for _, row in location_data.drop_duplicates().iterrows():
            lat = row.get('latitude')
            lon = row.get('longitude')
            region = row.get('region')
            
            if pd.notna(lat) and pd.notna(lon):
                existing = DimLocation.query.filter_by(latitude=lat, longitude=lon).first()
                if not existing:
                    # Find next available key
                    max_key = db.session.query(func.max(DimLocation.location_key)).scalar() or 0
                    dim_location = DimLocation(
                        location_key=max_key + 1,
                        latitude=float(lat),
                        longitude=float(lon),
                        region=region
                    )
                    db.session.add(dim_location)
                    count += 1
        db.session.commit()
        return count
    
    def _load_satellite_dimension(self, satellite_data):
        """Load satellite dimension"""
        count = 0
        for sensor in satellite_data['sensor_name'].dropna().unique():
            existing = DimSatellite.query.filter_by(sensor_name=sensor).first()
            if not existing:
                max_key = db.session.query(func.max(DimSatellite.satellite_key)).scalar() or 0
                dim_satellite = DimSatellite(
                    satellite_key=max_key + 1,
                    satellite_name='Unknown',
                    sensor_name=str(sensor),
                    spatial_resolution=None
                )
                db.session.add(dim_satellite)
                count += 1
        db.session.commit()
        return count
    
    def _load_source_dimension(self, dataset):
        """Load source dimension"""
        existing = DimSource.query.filter_by(provider=dataset.source_type).first()
        if not existing:
            max_key = db.session.query(func.max(DimSource.source_key)).scalar() or 0
            dim_source = DimSource(
                source_key=max_key + 1,
                provider=dataset.source_type,
                source_url=dataset.source_url,
                retrieval_date=datetime.utcnow().date()
            )
            db.session.add(dim_source)
            db.session.commit()
            return 1
        return 0
    
    def _load_fact_table(self, df, etl_job_id):
        """Load fact observation table"""
        count = 0
        for _, row in df.iterrows():
            # Get dimension keys
            date_key = None
            if 'observation_date' in df.columns and pd.notna(row['observation_date']):
                date = pd.to_datetime(row['observation_date'])
                date_key = int(date.strftime('%Y%m%d'))
            
            location_key = None
            if 'latitude' in df.columns and 'longitude' in df.columns:
                location = DimLocation.query.filter_by(
                    latitude=row['latitude'],
                    longitude=row['longitude']
                ).first()
                if location:
                    location_key = location.location_key
            
            satellite_key = None
            if 'sensor_name' in df.columns and pd.notna(row['sensor_name']):
                satellite = DimSatellite.query.filter_by(sensor_name=row['sensor_name']).first()
                if satellite:
                    satellite_key = satellite.satellite_key
            
            source_key = DimSource.query.first().source_key if DimSource.query.first() else None
            
            # Check if fact already exists
            if date_key and location_key and satellite_key and source_key:
                existing = FactObservation.query.filter_by(
                    date_key=date_key,
                    location_key=location_key,
                    satellite_key=satellite_key,
                    source_key=source_key
                ).first()
                
                if not existing:
                    max_key = db.session.query(func.max(FactObservation.observation_key)).scalar() or 0
                    fact = FactObservation(
                        observation_key=max_key + 1,
                        date_key=date_key,
                        location_key=location_key,
                        satellite_key=satellite_key,
                        source_key=source_key,
                        ndvi=row.get('ndvi'),
                        ndbi=row.get('ndbi'),
                        elevation=row.get('elevation'),
                        soil_moisture=row.get('soil_moisture'),
                        surface_temperature=row.get('surface_temperature'),
                        distance_from_water=row.get('distance_from_water'),
                        quality_flag='good'
                    )
                    db.session.add(fact)
                    count += 1
        
        db.session.commit()
        return count
    
    def execute_analytical_query(self, query_type):
        """Execute analytical queries on the warehouse"""
        if query_type == 'observations_by_region':
            results = db.session.query(
                DimLocation.region,
                func.count(FactObservation.observation_key)
            ).join(
                FactObservation, FactObservation.location_key == DimLocation.location_key
            ).group_by(DimLocation.region).all()
            
            return {
                'query_type': query_type,
                'results': [{'region': r[0] or 'Unknown', 'count': r[1]} for r in results]
            }
        
        elif query_type == 'monthly_trends':
            results = db.session.query(
                DimDate.month,
                DimDate.year,
                func.count(FactObservation.observation_key),
                func.avg(FactObservation.ndvi)
            ).join(
                FactObservation, FactObservation.date_key == DimDate.date_key
            ).group_by(DimDate.month, DimDate.year).order_by(DimDate.year, DimDate.month).all()
            
            return {
                'query_type': query_type,
                'results': [{
                    'month': r[0],
                    'year': r[1],
                    'count': r[2],
                    'avg_ndvi': float(r[3]) if r[3] else None
                } for r in results]
            }
        
        elif query_type == 'by_satellite':
            results = db.session.query(
                DimSatellite.satellite_name,
                DimSatellite.sensor_name,
                func.count(FactObservation.observation_key)
            ).join(
                FactObservation, FactObservation.satellite_key == DimSatellite.satellite_key
            ).group_by(DimSatellite.satellite_name, DimSatellite.sensor_name).all()
            
            return {
                'query_type': query_type,
                'results': [{
                    'satellite': r[0] or 'Unknown',
                    'sensor': r[1],
                    'count': r[2]
                } for r in results]
            }
        
        else:
            return {'error': f'Unknown query type: {query_type}'}
