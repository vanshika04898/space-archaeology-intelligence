from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import DatasetVersion, PreprocessingJob
from ..services.preprocessing_service import PreprocessingService
import uuid

bp = Blueprint('preprocessing', __name__)

@bp.route('/preview', methods=['POST'])
def preview_preprocessing():
    """Preview preprocessing transformations"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        configuration = data.get('configuration', {})
        
        service = PreprocessingService()
        result = service.preview_transformations(dataset_version_id, configuration)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/run', methods=['POST'])
def run_preprocessing():
    """Run preprocessing job and create new dataset version"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        configuration = data.get('configuration', {})
        
        # Create preprocessing job
        job = PreprocessingJob(
            dataset_version_id=dataset_version_id,
            configuration_json=configuration,
            status='running'
        )
        db.session.add(job)
        db.session.commit()
        
        # Run preprocessing
        service = PreprocessingService()
        try:
            result_version = service.run_preprocessing(dataset_version_id, configuration, job.id)
            job.status = 'completed'
            job.result_version_id = result_version.id
            job.completed_at = db.func.now()
            db.session.commit()
            
            return jsonify({
                'job_id': job.id,
                'status': 'completed',
                'result_version': result_version.to_dict()
            }), 201
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = db.func.now()
            db.session.commit()
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/jobs/<int:id>', methods=['GET'])
def get_preprocessing_job(id):
    """Get preprocessing job status"""
    try:
        job = PreprocessingJob.query.get_or_404(id)
        return jsonify(job.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
