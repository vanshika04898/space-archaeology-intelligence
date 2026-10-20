import pandas as pd
import numpy as np
from datetime import datetime, date
from ..extensions import db
from ..models import (
    Dataset, DatasetVersion, ETLJob, AuditLog,
    FactObservation, DimDate, DimLocation, DimSatellite, DimSite, DimSource
)

class ETLService:
    """Service for ETL operations and data warehouse loading"""
    
    def __init__(self):
        self.job_id = None
    
    def start_etl_job(self, source_dataset_id, job_name=None):
        """Start a new ETL job"""
        job = ETLJob(
            job_name=job_name or f"ETL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            source_dataset_id=source_dataset_id,
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(job)
        db.session.commit()
        self.job_id = job.id
        return job
    
    def update_job_status(self, status, rows_processed=0, error_message=None):
        """Update ETL job status"""
        if self.job_id:
            job = ETLJob.query.get(self.job_id)
            if job:
                job.status = status
                job.rows_processed = rows_processed
                job.error_message = error_message
                if status in ['completed', 'failed']:
                    job.completed_at = datetime.utcnow()
                db.session.commit()
    
    def log_audit(self, action, entity_type, entity_id, details=None):
        """Log an audit record"""
        log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow(),
            user_id='system'
        )
        db.session.add(log)
        db.session.commit()
    
    def extract_validate_transform(self, dataset_version_id):
        """Extract, validate, and transform data from dataset version"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        
        # Load data
        df = pd.read_csv(version.file_path)
        
        # Validation
        validation_results = {
            'total_rows': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values - report but don't impute
        missing_report = df.isnull().sum()
        
        return df, validation_results
    
    def get_or_create_date_dimension(self, date_value):
        """Get or create date dimension record"""
        if pd.isna(date_value):
            return None
        
        if isinstance(date_value, str):
            try:
                date_value = pd.to_datetime(date_value).date()
            except:
                return None
        
        date_key = int(date_value.strftime('%Y%m%d'))
        
        dim = DimDate.query.filter_by(date_key=date_key).first()
        if not dim:
            dim = DimDate(
                date_key=date_key,
                full_date=date_value,
                day=date_value.day,
                month=date_value.month,
                quarter=(date_value.month - 1) // 3 + 1,
                year=date_value.year,
                season=self._get_season(date_value.month)
            )
            db.session.add(dim)
            db.session.commit()
        
        return dim.date_key
    
    def _get_season(self, month):
        """Get season from month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def get_or_create_location_dimension(self, latitude, longitude, region=None, country=None):
        """Get or create location dimension record"""
        if pd.isna(latitude) or pd.isna(longitude):
            return None
        
        # Round coordinates to avoid excessive duplicates
        lat = round(float(latitude), 6)
        lon = round(float(longitude), 6)
        
        dim = DimLocation.query.filter_by(latitude=lat, longitude=lon).first()
        if not dim:
            dim = DimLocation(
                latitude=lat,
                longitude=lon,
                region=region,
                country=country
            )
            db.session.add(dim)
            db.session.commit()
        
        return dim.location_key
    
    def get_or_create_satellite_dimension(self, satellite_name, sensor_name=None, spatial_resolution=None, source_identifier=None):
        """Get or create satellite dimension record"""
        dim = DimSatellite.query.filter_by(satellite_name=satellite_name).first()
        if not dim:
            dim = DimSatellite(
                satellite_name=satellite_name,
                sensor_name=sensor_name,
                spatial_resolution=spatial_resolution,
                source_identifier=source_identifier
            )
            db.session.add(dim)
            db.session.commit()
        
        return dim.satellite_key
    
    def get_or_create_site_dimension(self, site_identifier, site_type=None, historical_period=None, verification_status='unverified'):
        """Get or create site dimension record"""
        dim = DimSite.query.filter_by(site_identifier=site_identifier).first()
        if not dim:
            dim = DimSite(
                site_identifier=site_identifier,
                site_type=site_type,
                historical_period=historical_period,
                verification_status=verification_status
            )
            db.session.add(dim)
            db.session.commit()
        
        return dim.site_key
    
    def get_or_create_source_dimension(self, provider, source_url=None, license=None, retrieval_date=None):
        """Get or create source dimension record"""
        dim = DimSource.query.filter_by(provider=provider).first()
        if not dim:
            dim = DimSource(
                provider=provider,
                source_url=source_url,
                license=license,
                retrieval_date=retrieval_date
            )
            db.session.add(dim)
            db.session.commit()
        
        return dim.source_key
    
    def load_warehouse(self, df, dataset_id):
        """Load data into warehouse fact and dimension tables"""
        rows_loaded = 0
        rows_rejected = 0
        
        for idx, row in df.iterrows():
            try:
                # Get dimension keys
                date_key = self.get_or_create_date_dimension(row.get('observation_date'))
                location_key = self.get_or_create_location_dimension(
                    row.get('latitude'),
                    row.get('longitude'),
                    row.get('region'),
                    row.get('country')
                )
                satellite_key = self.get_or_create_satellite_dimension(
                    row.get('satellite_name', 'Unknown'),
                    row.get('sensor_name'),
                    row.get('spatial_resolution'),
                    row.get('source_identifier')
                )
                source_key = self.get_or_create_source_dimension(
                    row.get('provider', 'Unknown'),
                    row.get('source_url'),
                    row.get('license'),
                    row.get('retrieval_date')
                )
                
                # Site key is optional
                site_key = None
                if pd.notna(row.get('site_identifier')):
                    site_key = self.get_or_create_site_dimension(
                        row['site_identifier'],
                        row.get('site_type'),
                        row.get('historical_period'),
                        row.get('verification_status', 'unverified')
                    )
                
                # Check for duplicate fact
                existing = FactObservation.query.filter_by(
                    date_key=date_key,
                    location_key=location_key,
                    satellite_key=satellite_key,
                    source_key=source_key
                ).first()
                
                if existing:
                    # Update existing record
                    existing.ndvi = row.get('ndvi')
                    existing.ndbi = row.get('ndbi')
                    existing.elevation = row.get('elevation')
                    existing.soil_moisture = row.get('soil_moisture')
                    existing.surface_temperature = row.get('surface_temperature')
                    existing.distance_from_water = row.get('distance_from_water')
                    existing.observation_count += 1
                else:
                    # Create new fact record
                    fact = FactObservation(
                        date_key=date_key,
                        location_key=location_key,
                        satellite_key=satellite_key,
                        site_key=site_key,
                        source_key=source_key,
                        ndvi=row.get('ndvi'),
                        ndbi=row.get('ndbi'),
                        elevation=row.get('elevation'),
                        soil_moisture=row.get('soil_moisture'),
                        surface_temperature=row.get('surface_temperature'),
                        distance_from_water=row.get('distance_from_water'),
                        quality_flag=row.get('quality_flag', 'good'),
                        observation_count=1
                    )
                    db.session.add(fact)
                
                rows_loaded += 1
                
                # Commit every 100 rows to avoid large transactions
                if rows_loaded % 100 == 0:
                    db.session.commit()
                    
            except Exception as e:
                rows_rejected += 1
                print(f"Error loading row {idx}: {str(e)}")
                continue
        
        db.session.commit()
        
        return {
            'rows_loaded': rows_loaded,
            'rows_rejected': rows_rejected,
            'total_processed': rows_loaded + rows_rejected
        }
    
    def run_etl(self, dataset_version_id):
        """Run complete ETL pipeline"""
        try:
            # Start job
            dataset_version = DatasetVersion.query.get(dataset_version_id)
            job = self.start_etl_job(dataset_version.dataset_id, f"ETL_Dataset_{dataset_version_id}")
            
            # Extract, validate, transform
            df, validation_results = self.extract_validate_transform(dataset_version_id)
            
            # Load warehouse
            load_results = self.load_warehouse(df, dataset_version.dataset_id)
            
            # Update job status
            self.update_job_status('completed', load_results['rows_loaded'])
            
            # Log audit
            self.log_audit('ETL_COMPLETE', 'ETLJob', job.id, {
                'validation': validation_results,
                'load_results': load_results
            })
            
            return {
                'status': 'success',
                'job_id': job.id,
                'validation': validation_results,
                'load_results': load_results
            }
            
        except Exception as e:
            self.update_job_status('failed', error_message=str(e))
            self.log_audit('ETL_FAILED', 'ETLJob', self.job_id, {'error': str(e)})
            raise
    
    def get_etl_jobs(self, limit=50):
        """Get recent ETL jobs"""
        jobs = ETLJob.query.order_by(ETLJob.started_at.desc()).limit(limit).all()
        return [job.to_dict() for job in jobs]
    
    def get_etl_job(self, job_id):
        """Get specific ETL job"""
        job = ETLJob.query.get_or_404(job_id)
        return job.to_dict()
