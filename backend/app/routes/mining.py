from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import MiningRun
from ..services.mining_service import MiningService

bp = Blueprint('mining', __name__)

@bp.route('/algorithms', methods=['GET'])
def get_algorithms():
    """Get list of available algorithms"""
    try:
        service = MiningService()
        algorithms = service.get_available_algorithms()
        return jsonify(algorithms), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/run', methods=['POST'])
def run_mining():
    """Execute a data mining algorithm"""
    try:
        data = request.json
        dataset_version_id = data.get('dataset_version_id')
        algorithm_name = data.get('algorithm_name')
        algorithm_family = data.get('algorithm_family')
        parameters = data.get('parameters', {})
        selected_features = data.get('selected_features', [])
        
        # Create mining run record
        run = MiningRun(
            dataset_version_id=dataset_version_id,
            algorithm_name=algorithm_name,
            algorithm_family=algorithm_family,
            parameters_json=parameters,
            selected_features_json=selected_features,
            status='running'
        )
        db.session.add(run)
        db.session.commit()
        
        # Execute algorithm
        service = MiningService()
        try:
            result = service.execute_algorithm(
                dataset_version_id,
                algorithm_name,
                algorithm_family,
                parameters,
                selected_features,
                run.id
            )
            
            run.status = 'completed'
            run.metrics_json = result.get('metrics')
            run.result_location = result.get('result_location')
            run.completed_at = db.func.now()
            db.session.commit()
            
            return jsonify({
                'run_id': run.id,
                'status': 'completed',
                'result': result
            }), 201
        except Exception as e:
            run.status = 'failed'
            run.error_message = str(e)
            run.completed_at = db.func.now()
            db.session.commit()
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/runs', methods=['GET'])
def get_mining_runs():
    """Get all mining runs"""
    try:
        runs = MiningRun.query.order_by(MiningRun.created_at.desc()).limit(50).all()
        return jsonify([r.to_dict() for r in runs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/runs/<int:id>', methods=['GET'])
def get_mining_run(id):
    """Get a specific mining run"""
    try:
        run = MiningRun.query.get_or_404(id)
        return jsonify(run.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/runs/<int:id>/results', methods=['GET'])
def get_mining_results(id):
    """Get detailed results of a mining run"""
    try:
        run = MiningRun.query.get_or_404(id)
        service = MiningService()
        results = service.load_results(run.result_location)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
