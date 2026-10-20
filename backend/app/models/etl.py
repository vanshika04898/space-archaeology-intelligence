from datetime import datetime
from ..extensions import db

class ETLJob(db.Model):
    __tablename__ = 'etl_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    source_dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=True, index=True)
    job_type = db.Column(db.String(50), nullable=False)  # full_load, incremental, refresh
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, running, completed, failed
    rows_read = db.Column(db.Integer, default=0)
    rows_inserted = db.Column(db.Integer, default=0)
    rows_rejected = db.Column(db.Integer, default=0)
    error_summary = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_dataset_id': self.source_dataset_id,
            'job_type': self.job_type,
            'status': self.status,
            'rows_read': self.rows_read,
            'rows_inserted': self.rows_inserted,
            'rows_rejected': self.rows_rejected,
            'error_summary': self.error_summary,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)  # upload, preprocess, train, predict, etc.
    resource_type = db.Column(db.String(50), nullable=False)  # dataset, model, job, etc.
    resource_id = db.Column(db.Integer)
    details_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details_json': self.details_json,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
