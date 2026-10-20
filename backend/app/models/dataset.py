from datetime import datetime
from ..extensions import db

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(50), nullable=False)  # csv, geojson, raster, etc.
    source_url = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    storage_key = db.Column(db.String(500))
    schema_json = db.Column(db.JSON)
    record_count = db.Column(db.Integer, default=0)
    provenance = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    versions = db.relationship('DatasetVersion', backref='dataset', lazy=True, cascade='all, delete-orphan')
    quality_reports = db.relationship('DataQualityReport', backref='dataset', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'schema_json': self.schema_json,
            'record_count': self.record_count,
            'provenance': self.provenance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'version_count': len(self.versions)
        }

class DatasetVersion(db.Model):
    __tablename__ = 'dataset_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    parent_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=True)
    transformation_summary = db.Column(db.JSON)
    file_path = db.Column(db.String(500))
    record_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    parent_version = db.relationship('DatasetVersion', remote_side=[id], backref='child_versions')
    preprocessing_jobs = db.relationship('PreprocessingJob', foreign_keys='PreprocessingJob.dataset_version_id', backref='dataset_version', lazy=True)
    mining_runs = db.relationship('MiningRun', backref='dataset_version', lazy=True)
    quality_reports = db.relationship('DataQualityReport', backref='dataset_version', lazy=True)
    
    # Unique constraint on dataset_id + version_number
    __table_args__ = (db.UniqueConstraint('dataset_id', 'version_number', name='unique_dataset_version'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'version_number': self.version_number,
            'parent_version_id': self.parent_version_id,
            'transformation_summary': self.transformation_summary,
            'record_count': self.record_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DataQualityReport(db.Model):
    __tablename__ = 'data_quality_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=True, index=True)
    dataset_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=True, index=True)
    missing_value_count = db.Column(db.Integer, default=0)
    duplicate_count = db.Column(db.Integer, default=0)
    invalid_coordinate_count = db.Column(db.Integer, default=0)
    validation_summary = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'dataset_version_id': self.dataset_version_id,
            'missing_value_count': self.missing_value_count,
            'duplicate_count': self.duplicate_count,
            'invalid_coordinate_count': self.invalid_coordinate_count,
            'validation_summary': self.validation_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
