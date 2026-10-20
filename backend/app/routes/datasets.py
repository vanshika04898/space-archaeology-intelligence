from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
from ..extensions import db
from ..models import Dataset, DatasetVersion, DataQualityReport
from ..services.dataset_service import DatasetService
import uuid

bp = Blueprint('datasets', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('', methods=['GET'])
def get_datasets():
    """Get all datasets"""
    try:
        datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
        return jsonify([d.to_dict() for d in datasets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_dataset(id):
    """Get a specific dataset"""
    try:
        dataset = Dataset.query.get_or_404(id)
        return jsonify(dataset.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload a CSV dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: csv, geojson, json'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Read and validate the file
        if file_extension == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_json(file_path)
        
        # Get schema
        schema = {
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'row_count': len(df),
            'column_count': len(df.columns)
        }
        
        # Create dataset record
        dataset = Dataset(
            name=request.form.get('name', original_filename),
            description=request.form.get('description', ''),
            source_type=file_extension,
            file_path=file_path,
            storage_key=unique_filename,
            schema_json=schema,
            record_count=len(df),
            provenance=f"Uploaded on {datetime.utcnow().isoformat()}"
        )
        db.session.add(dataset)
        db.session.commit()
        
        # Create initial version
        version = DatasetVersion(
            dataset_id=dataset.id,
            version_number=1,
            file_path=file_path,
            record_count=len(df),
            transformation_summary={'type': 'initial_import'}
        )
        db.session.add(version)
        db.session.commit()
        
        # Generate quality report
        service = DatasetService()
        quality_report = service.generate_quality_report(df, dataset.id, version.id)
        
        return jsonify({
            'dataset': dataset.to_dict(),
            'version': version.to_dict(),
            'quality_report': quality_report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/preview', methods=['GET'])
def preview_dataset(id):
    """Preview first 100 rows of a dataset"""
    try:
        dataset = Dataset.query.get_or_404(id)
        if not dataset.file_path or not os.path.exists(dataset.file_path):
            return jsonify({'error': 'Dataset file not found'}), 404
        
        if dataset.source_type == 'csv':
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_json(dataset.file_path)
        
        preview = df.head(100).to_dict(orient='records')
        return jsonify({
            'preview': preview,
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/profile', methods=['GET'])
def profile_dataset(id):
    """Get dataset profile with statistics"""
    try:
        dataset = Dataset.query.get_or_404(id)
        if not dataset.file_path or not os.path.exists(dataset.file_path):
            return jsonify({'error': 'Dataset file not found'}), 404
        
        if dataset.source_type == 'csv':
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_json(dataset.file_path)
        
        # Generate profile
        profile = {
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_counts': df.isnull().sum().to_dict(),
            'unique_counts': df.nunique().to_dict(),
            'numeric_stats': {}
        }
        
        # Add statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            profile['numeric_stats'][col] = {
                'mean': float(df[col].mean()) if not df[col].empty else None,
                'std': float(df[col].std()) if not df[col].empty else None,
                'min': float(df[col].min()) if not df[col].empty else None,
                'max': float(df[col].max()) if not df[col].empty else None,
                'median': float(df[col].median()) if not df[col].empty else None
            }
        
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/quality', methods=['GET'])
def quality_dataset(id):
    """Get latest quality report for a dataset"""
    try:
        dataset = Dataset.query.get_or_404(id)
        report = DataQualityReport.query.filter_by(dataset_id=id).order_by(
            DataQualityReport.created_at.desc()
        ).first()
        
        if not report:
            return jsonify({'error': 'No quality report found'}), 404
        
        return jsonify(report.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/download', methods=['GET'])
def download_dataset(id):
    """Get download URL for a dataset"""
    try:
        dataset = Dataset.query.get_or_404(id)
        return jsonify({
            'filename': os.path.basename(dataset.file_path),
            'download_url': f'/api/v1/datasets/{id}/file'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
