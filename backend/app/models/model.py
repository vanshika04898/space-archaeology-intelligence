from datetime import datetime
from ..extensions import db

class ModelRegistry(db.Model):
    __tablename__ = 'model_registry'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    algorithm_name = db.Column(db.String(100), nullable=False)
    dataset_version_id = db.Column(db.Integer, db.ForeignKey('dataset_versions.id'), nullable=False, index=True)
    artifact_path = db.Column(db.String(500), nullable=False)
    feature_schema_json = db.Column(db.JSON, nullable=False)
    preprocessing_config_json = db.Column(db.JSON)
    metrics_json = db.Column(db.JSON)
    model_version = db.Column(db.String(50), nullable=False)
    training_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, deprecated, retired
    
    # Relationships
    predictions = db.relationship('Prediction', backref='model', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'algorithm_name': self.algorithm_name,
            'dataset_version_id': self.dataset_version_id,
            'artifact_path': self.artifact_path,
            'feature_schema_json': self.feature_schema_json,
            'preprocessing_config_json': self.preprocessing_config_json,
            'metrics_json': self.metrics_json,
            'model_version': self.model_version,
            'training_timestamp': self.training_timestamp.isoformat() if self.training_timestamp else None,
            'status': self.status,
            'prediction_count': len(self.predictions)
        }

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model_registry.id'), nullable=False, index=True)
    record_id = db.Column(db.String(100), nullable=False)
    predicted_class = db.Column(db.String(100))
    predicted_probability = db.Column(db.Float)
    prediction_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    prediction_source = db.Column(db.String(50))  # batch, api, scheduled
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'record_id': self.record_id,
            'predicted_class': self.predicted_class,
            'predicted_probability': self.predicted_probability,
            'prediction_timestamp': self.prediction_timestamp.isoformat() if self.prediction_timestamp else None,
            'prediction_source': self.prediction_source
        }
