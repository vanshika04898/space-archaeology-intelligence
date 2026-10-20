from flask import Blueprint, jsonify
from ..extensions import db

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'service': 'space-archaeology-intelligence-api'
    }), 200
