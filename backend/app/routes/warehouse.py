from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import ETLJob, FactObservation, DimDate, DimLocation, DimSatellite, DimSite, DimSource
from ..services.warehouse_service import WarehouseService

bp = Blueprint('warehouse', __name__)

@bp.route('/schema', methods=['GET'])
def get_warehouse_schema():
    """Get data warehouse schema information"""
    try:
        service = WarehouseService()
        schema = service.get_schema()
        return jsonify(schema), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/summary', methods=['GET'])
def get_warehouse_summary():
    """Get data warehouse summary statistics"""
    try:
        service = WarehouseService()
        summary = service.get_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/etl/jobs', methods=['GET'])
def get_etl_jobs():
    """Get ETL job history"""
    try:
        jobs = ETLJob.query.order_by(ETLJob.started_at.desc()).limit(50).all()
        return jsonify([j.to_dict() for j in jobs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/etl/run', methods=['POST'])
def run_etl():
    """Run ETL job to load data into warehouse"""
    try:
        data = request.json
        source_dataset_id = data.get('source_dataset_id')
        job_type = data.get('job_type', 'full_load')
        
        service = WarehouseService()
        result = service.run_etl(source_dataset_id, job_type)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Execute analytical queries on the warehouse"""
    try:
        query_type = request.args.get('query_type', 'observations_by_region')
        service = WarehouseService()
        result = service.execute_analytical_query(query_type)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
