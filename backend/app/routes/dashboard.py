from flask import Blueprint, jsonify
from ..extensions import db
from ..models import Dataset, DatasetVersion, ModelRegistry, ETLJob, DataQualityReport, ReferenceSite
from sqlalchemy import func, desc

bp = Blueprint('dashboard', __name__)

@bp.route('/summary', methods=['GET'])
def get_summary():
    """Get dashboard summary statistics"""
    try:
        total_records = db.session.query(func.sum(Dataset.record_count)).scalar() or 0
        
        verified_sites = db.session.query(func.count(ReferenceSite.id)).filter(
            ReferenceSite.verification_status == 'verified'
        ).scalar() or 0
        
        candidate_locations = db.session.query(func.count(ReferenceSite.id)).filter(
            ReferenceSite.verification_status == 'unverified'
        ).scalar() or 0
        
        regions = db.session.query(func.count(func.distinct(DatasetVersion.id))).scalar() or 0
        
        trained_models = db.session.query(func.count(ModelRegistry.id)).filter(
            ModelRegistry.status == 'active'
        ).scalar() or 0
        
        latest_etl = db.session.query(ETLJob).order_by(desc(ETLJob.started_at)).first()
        etl_status = latest_etl.status if latest_etl else 'no_jobs'
        
        last_training = db.session.query(func.max(ModelRegistry.training_timestamp)).scalar()
        
        quality_issues = db.session.query(func.sum(DataQualityReport.missing_value_count)).scalar() or 0
        quality_issues += db.session.query(func.sum(DataQualityReport.duplicate_count)).scalar() or 0
        quality_issues += db.session.query(func.sum(DataQualityReport.invalid_coordinate_count)).scalar() or 0
        
        return jsonify({
            'total_records': total_records,
            'verified_sites': verified_sites,
            'candidate_locations': candidate_locations,
            'distinct_regions': regions,
            'trained_models': trained_models,
            'latest_etl_status': etl_status,
            'last_model_training': last_training.isoformat() if last_training else None,
            'data_quality_issues': quality_issues
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/charts', methods=['GET'])
def get_charts():
    """Get dashboard chart data"""
    try:
        # Records by region (simulated from datasets)
        datasets = db.session.query(Dataset.name, Dataset.record_count).all()
        region_data = [{'name': d[0], 'count': d[1] or 0} for d in datasets]
        
        # Records by archaeological class (from reference sites)
        site_types = db.session.query(
            ReferenceSite.site_type,
            func.count(ReferenceSite.id)
        ).group_by(ReferenceSite.site_type).all()
        class_data = [{'name': st[0] or 'Unknown', 'count': st[1]} for st in site_types]
        
        # ETL job history
        etl_jobs = db.session.query(
            ETLJob.job_type,
            ETLJob.status,
            ETLJob.rows_inserted,
            ETLJob.started_at
        ).order_by(desc(ETLJob.started_at)).limit(10).all()
        etl_data = [{
            'job_type': j[0],
            'status': j[1],
            'rows_inserted': j[2],
            'started_at': j[3].isoformat() if j[3] else None
        } for j in etl_jobs]
        
        # Model training history
        models = db.session.query(
            ModelRegistry.algorithm_name,
            ModelRegistry.metrics_json,
            ModelRegistry.training_timestamp
        ).order_by(desc(ModelRegistry.training_timestamp)).limit(10).all()
        model_data = [{
            'algorithm': m[0],
            'metrics': m[1],
            'training_timestamp': m[2].isoformat() if m[2] else None
        } for m in models]
        
        return jsonify({
            'region_distribution': region_data,
            'archaeological_class_distribution': class_data,
            'etl_history': etl_data,
            'model_training_history': model_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
