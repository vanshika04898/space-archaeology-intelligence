from datetime import datetime
from ..extensions import db

class ReferenceSite(db.Model):
    __tablename__ = 'reference_sites'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(100))
    site_type = db.Column(db.String(100))
    source_url = db.Column(db.String(500))
    verification_status = db.Column(db.String(20), default='unverified')  # verified, unverified, disputed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Index for spatial queries
    __table_args__ = (
        db.Index('idx_reference_location', 'latitude', 'longitude'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_name': self.site_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'region': self.region,
            'site_type': self.site_type,
            'source_url': self.source_url,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DataSource(db.Model):
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(200))
    source_url = db.Column(db.String(500))
    license = db.Column(db.String(200))
    retrieval_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'source_url': self.source_url,
            'license': self.license,
            'retrieval_date': self.retrieval_date.isoformat() if self.retrieval_date else None,
            'description': self.description
        }
