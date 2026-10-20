from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Dataset, DataQualityReport, MiningRun, ModelRegistry, ETLJob
import pandas as pd
from datetime import datetime

bp = Blueprint('reports', __name__)

@bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate a downloadable report"""
    try:
        data = request.json
        report_type = data.get('report_type')
        dataset_id = data.get('dataset_id')
        model_id = data.get('model_id')
        mining_run_id = data.get('mining_run_id')
        
        if report_type == 'dataset_profile':
            report = self._generate_dataset_profile(dataset_id)
        elif report_type == 'data_quality':
            report = self._generate_data_quality_report(dataset_id)
        elif report_type == 'mining_results':
            report = self._generate_mining_report(mining_run_id)
        elif report_type == 'model_evaluation':
            report = self._generate_model_evaluation_report(model_id)
        elif report_type == 'warehouse_summary':
            report = self._generate_warehouse_summary()
        else:
            return jsonify({'error': f'Unknown report type: {report_type}'}), 400
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_report(id):
    """Get a previously generated report"""
    try:
        # In a full implementation, this would retrieve from a reports table
        return jsonify({'error': 'Report storage not implemented'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_dataset_profile(self, dataset_id):
    """Generate dataset profile report"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    return {
        'report_type': 'dataset_profile',
        'generated_at': datetime.utcnow().isoformat(),
        'dataset': dataset.to_dict(),
        'schema': dataset.schema_json
    }

def _generate_data_quality_report(self, dataset_id):
    """Generate data quality report"""
    dataset = Dataset.query.get_or_404(dataset_id)
    quality_report = DataQualityReport.query.filter_by(dataset_id=dataset_id).order_by(
        DataQualityReport.created_at.desc()
    ).first()
    
    return {
        'report_type': 'data_quality',
        'generated_at': datetime.utcnow().isoformat(),
        'dataset': dataset.to_dict(),
        'quality_report': quality_report.to_dict() if quality_report else None
    }

def _generate_mining_report(self, mining_run_id):
    """Generate mining results report"""
    mining_run = MiningRun.query.get_or_404(mining_run_id)
    
    return {
        'report_type': 'mining_results',
        'generated_at': datetime.utcnow().isoformat(),
        'mining_run': mining_run.to_dict(),
        'metrics': mining_run.metrics_json
    }

def _generate_model_evaluation_report(self, model_id):
    """Generate model evaluation report"""
    model = ModelRegistry.query.get_or_404(model_id)
    
    return {
        'report_type': 'model_evaluation',
        'generated_at': datetime.utcnow().isoformat(),
        'model': model.to_dict(),
        'metrics': model.metrics_json
    }

def _generate_warehouse_summary(self):
    """Generate warehouse summary report"""
    from ..models import FactObservation, DimDate, DimLocation, DimSatellite
    from sqlalchemy import func
    
    return {
        'report_type': 'warehouse_summary',
        'generated_at': datetime.utcnow().isoformat(),
        'fact_count': db.session.query(func.count(FactObservation.observation_key)).scalar() or 0,
        'date_count': db.session.query(DimDate).count(),
        'location_count': db.session.query(DimLocation).count(),
        'satellite_count': db.session.query(DimSatellite).count()
    }
