from datetime import datetime
from ..extensions import db

class DimDate(db.Model):
    __tablename__ = 'dim_date'
    
    date_key = db.Column(db.Integer, primary_key=True)  # YYYYMMDD format
    full_date = db.Column(db.Date, nullable=False, unique=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season = db.Column(db.String(20))  # spring, summer, fall, winter
    
    def to_dict(self):
        return {
            'date_key': self.date_key,
            'full_date': self.full_date.isoformat() if self.full_date else None,
            'day': self.day,
            'month': self.month,
            'quarter': self.quarter,
            'year': self.year,
            'season': self.season
        }

class DimLocation(db.Model):
    __tablename__ = 'dim_location'
    
    location_key = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    
    __table_args__ = (
        db.Index('idx_location_coords', 'latitude', 'longitude'),
    )
    
    def to_dict(self):
        return {
            'location_key': self.location_key,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'region': self.region,
            'country': self.country
        }

class DimSatellite(db.Model):
    __tablename__ = 'dim_satellite'
    
    satellite_key = db.Column(db.Integer, primary_key=True)
    satellite_name = db.Column(db.String(100), nullable=False)
    sensor_name = db.Column(db.String(100))
    spatial_resolution = db.Column(db.Float)
    source_identifier = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'satellite_key': self.satellite_key,
            'satellite_name': self.satellite_name,
            'sensor_name': self.sensor_name,
            'spatial_resolution': self.spatial_resolution,
            'source_identifier': self.source_identifier
        }

class DimSite(db.Model):
    __tablename__ = 'dim_site'
    
    site_key = db.Column(db.Integer, primary_key=True)
    site_identifier = db.Column(db.String(200), nullable=False)
    site_type = db.Column(db.String(100))
    historical_period = db.Column(db.String(100))
    verification_status = db.Column(db.String(20), default='unverified')
    
    def to_dict(self):
        return {
            'site_key': self.site_key,
            'site_identifier': self.site_identifier,
            'site_type': self.site_type,
            'historical_period': self.historical_period,
            'verification_status': self.verification_status
        }

class DimSource(db.Model):
    __tablename__ = 'dim_source'
    
    source_key = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(500))
    license = db.Column(db.String(200))
    retrieval_date = db.Column(db.Date)
    
    def to_dict(self):
        return {
            'source_key': self.source_key,
            'provider': self.provider,
            'source_url': self.source_url,
            'license': self.license,
            'retrieval_date': self.retrieval_date.isoformat() if self.retrieval_date else None
        }

class FactObservation(db.Model):
    __tablename__ = 'fact_observation'
    
    observation_key = db.Column(db.Integer, primary_key=True)
    date_key = db.Column(db.Integer, db.ForeignKey('dim_date.date_key'), nullable=False, index=True)
    location_key = db.Column(db.Integer, db.ForeignKey('dim_location.location_key'), nullable=False, index=True)
    satellite_key = db.Column(db.Integer, db.ForeignKey('dim_satellite.satellite_key'), nullable=False, index=True)
    site_key = db.Column(db.Integer, db.ForeignKey('dim_site.site_key'), nullable=True, index=True)
    source_key = db.Column(db.Integer, db.ForeignKey('dim_source.source_key'), nullable=False, index=True)
    
    # Measurements
    ndvi = db.Column(db.Float)
    ndbi = db.Column(db.Float)
    elevation = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    surface_temperature = db.Column(db.Float)
    distance_from_water = db.Column(db.Float)
    
    # Quality flags
    quality_flag = db.Column(db.String(20), default='good')  # good, suspect, poor
    observation_count = db.Column(db.Integer, default=1)
    
    # Relationships
    date = db.relationship('DimDate', backref='observations')
    location = db.relationship('DimLocation', backref='observations')
    satellite = db.relationship('DimSatellite', backref='observations')
    site = db.relationship('DimSite', backref='observations')
    source = db.relationship('DimSource', backref='observations')
    
    # Unique constraint to prevent duplicate fact rows
    __table_args__ = (
        db.UniqueConstraint('date_key', 'location_key', 'satellite_key', 'source_key', name='unique_observation'),
    )
    
    def to_dict(self):
        return {
            'observation_key': self.observation_key,
            'date_key': self.date_key,
            'location_key': self.location_key,
            'satellite_key': self.satellite_key,
            'site_key': self.site_key,
            'source_key': self.source_key,
            'ndvi': self.ndvi,
            'ndbi': self.ndbi,
            'elevation': self.elevation,
            'soil_moisture': self.soil_moisture,
            'surface_temperature': self.surface_temperature,
            'distance_from_water': self.distance_from_water,
            'quality_flag': self.quality_flag,
            'observation_count': self.observation_count
        }
