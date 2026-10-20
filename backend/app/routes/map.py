from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models import ReferenceSite, DatasetVersion, Prediction
from ..models import ModelRegistry

bp = Blueprint('map', __name__)

@bp.route('/observations', methods=['GET'])
def get_observations():
    """Get observation locations for map display"""
    try:
        dataset_version_id = int(request.args.get('dataset_version_id')) if request.args.get('dataset_version_id') else None
        
        if dataset_version_id:
            version = DatasetVersion.query.get_or_404(dataset_version_id)
            # Load from CSV and extract coordinates
            import pandas as pd
            df = pd.read_csv(version.file_path)
            
            observations = []
            if 'latitude' in df.columns and 'longitude' in df.columns:
                for _, row in df.head(1000).iterrows():  # Limit to 1000 for performance
                    observations.append({
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'record_id': row.get('record_id', f"obs_{_}"),
                        'ndvi': float(row['ndvi']) if 'ndvi' in row and pd.notna(row['ndvi']) else None,
                        'elevation': float(row['elevation']) if 'elevation' in row and pd.notna(row['elevation']) else None,
                        'site_type': row.get('site_type'),
                        'observation_date': str(row.get('observation_date')) if 'observation_date' in row else None
                    })
            
            return jsonify(observations), 200
        else:
            return jsonify({'error': 'dataset_version_id required'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/candidates', methods=['GET'])
def get_candidates():
    """Get candidate locations from model predictions"""
    try:
        model_id = int(request.args.get('model_id')) if request.args.get('model_id') else None
        
        if model_id:
            model = ModelRegistry.query.get_or_404(model_id)
            predictions = Prediction.query.filter_by(model_id=model_id).limit(500).all()
            
            candidates = []
            for pred in predictions:
                candidates.append({
                    'record_id': pred.record_id,
                    'predicted_class': pred.predicted_class,
                    'predicted_probability': pred.predicted_probability,
                    'prediction_timestamp': pred.prediction_timestamp.isoformat() if pred.prediction_timestamp else None,
                    'model_name': model.name
                })
            
            return jsonify(candidates), 200
        else:
            return jsonify([]), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reference-sites', methods=['GET'])
def get_reference_sites():
    """Get verified reference archaeological sites"""
    try:
        sites = ReferenceSite.query.all()
        
        return jsonify([{
            'id': s.id,
            'site_name': s.site_name,
            'latitude': s.latitude,
            'longitude': s.longitude,
            'region': s.region,
            'site_type': s.site_type,
            'verification_status': s.verification_status,
            'source_url': s.source_url
        } for s in sites]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
