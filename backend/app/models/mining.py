from datetime import datetime
from ..extensions import db

class MiningRun(db.Model):
    __tablename__ = 'mining_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    dataset_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=False, index=True)
    algorithm_name = db.Column(db.String(100), nullable=False)
    algorithm_family = db.Column(db.String(50), nullable=False)  # classification, regression, clustering, etc.
    parameters_json = db.Column(db.JSON, nullable=False)
    selected_features_json = db.Column(db.JSON)
    metrics_json = db.Column(db.JSON)
    result_location = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, running, completed, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dataset_version_id': self.dataset_version_id,
            'algorithm_name': self.algorithm_name,
            'algorithm_family': self.algorithm_family,
            'parameters_json': self.parameters_json,
            'selected_features_json': self.selected_features_json,
            'metrics_json': self.metrics_json,
            'result_location': self.result_location,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
