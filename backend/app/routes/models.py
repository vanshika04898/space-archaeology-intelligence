from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import ModelRegistry, Prediction, DatasetVersion
from ..services.model_service import ModelService
import joblib
import os

bp = Blueprint('models', __name__)

@bp.route('', methods=['GET'])
def get_models():
    """Get all registered models"""
    try:
        models = ModelRegistry.query.order_by(ModelRegistry.training_timestamp.desc()).all()
        return jsonify([m.to_dict() for m in models]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_model(id):
    """Get a specific model"""
    try:
        model = ModelRegistry.query.get_or_404(id)
        return jsonify(model.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/train', methods=['POST'])
def train_model():
    """Train a new model"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        algorithm_name = data.get('algorithm_name')
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns', [])
        parameters = data.get('parameters', {})
        model_name = data.get('model_name', f"{algorithm_name}_model")
        
        service = ModelService()
        result = service.train_model(
            dataset_version_id,
            algorithm_name,
            target_column,
            feature_columns,
            parameters,
            model_name
        )
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/predict', methods=['POST'])
def predict(id):
    """Make predictions using a trained model"""
    try:
        data = request.json
        records = data.get('records', [])
        
        model = ModelRegistry.query.get_or_404(id)
        service = ModelService()
        predictions = service.predict(model, records)
        
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/evaluate', methods=['POST'])
def evaluate_model(id):
    """Evaluate a model on test data"""
    try:
        data = request.json
        test_dataset_version_id = data.get('test_dataset_version_id')
        
        model = ModelRegistry.query.get_or_404(id)
        service = ModelService()
        evaluation = service.evaluate_model(model, test_dataset_version_id)
        
        return jsonify(evaluation), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/metrics', methods=['GET'])
def get_model_metrics(id):
    """Get model metrics"""
    try:
        model = ModelRegistry.query.get_or_404(id)
        return jsonify(model.metrics_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
