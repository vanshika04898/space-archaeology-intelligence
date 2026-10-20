from flask import Blueprint, request, jsonify
from ..services.feature_service import FeatureService

bp = Blueprint('features', __name__)

@bp.route('/available', methods=['GET'])
def get_available_features():
    """Get list of available feature engineering options"""
    try:
        service = FeatureService()
        features = service.get_available_features()
        return jsonify(features), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/preview', methods=['POST'])
def preview_features():
    """Preview feature engineering transformations"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        feature_config = data.get('features', [])
        
        service = FeatureService()
        result = service.preview_features(dataset_version_id, feature_config)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/generate', methods=['POST'])
def generate_features():
    """Generate features and create new dataset version"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        feature_config = data.get('features', [])
        
        service = FeatureService()
        result = service.generate_features(dataset_version_id, feature_config)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
