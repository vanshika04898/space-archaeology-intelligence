from flask import Flask
from .config import config
from .extensions import db, migrate, cors
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from .routes import health_bp, datasets_bp, preprocessing_bp, features_bp, mining_bp, models_bp, warehouse_bp, map_routes, reports_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(datasets_bp, url_prefix='/api/v1/datasets')
    app.register_blueprint(preprocessing_bp, url_prefix='/api/v1/preprocessing')
    app.register_blueprint(features_bp, url_prefix='/api/v1/features')
    app.register_blueprint(mining_bp, url_prefix='/api/v1/mining')
    app.register_blueprint(models_bp, url_prefix='/api/v1/models')
    app.register_blueprint(warehouse_bp, url_prefix='/api/v1/warehouse')
    app.register_blueprint(map_routes, url_prefix='/api/v1/map')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    
    from .routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    
    return app
