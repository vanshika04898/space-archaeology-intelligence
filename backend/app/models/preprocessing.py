from datetime import datetime
from ..extensions import db

class PreprocessingJob(db.Model):
    __tablename__ = 'preprocessing_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=False, index=True)
    configuration_json = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, running, completed, failed
    result_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    result_version = db.relationship('DatasetVersion', foreign_keys=[result_version_id], backref='preprocessing_source')
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_version_id': self.dataset_version_id,
            'configuration_json': self.configuration_json,
            'status': self.status,
            'result_version_id': self.result_version_id,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
