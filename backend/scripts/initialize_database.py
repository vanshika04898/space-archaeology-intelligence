"""
Initialize the database with all tables.
Run this script to create the database schema.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    User, Dataset, DatasetVersion, DataQualityReport,
    PreprocessingJob, MiningRun, ModelRegistry, Prediction,
    ETLJob, AuditLog, ReferenceSite, DataSource,
    FactObservation, DimDate, DimLocation, DimSatellite, DimSite, DimSource
)

def init_db():
    """Initialize the database with all tables"""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")
        
        # Create default admin user
        admin = User.query.filter_by(email='admin@space-archaeology.local').first()
        if not admin:
            admin = User(
                name='Admin User',
                email='admin@space-archaeology.local',
                role='admin'
            )
            admin.set_password('admin123')  # Change in production
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (email: admin@space-archaeology.local, password: admin123)")
        
        print("\nDatabase initialization complete.")

if __name__ == '__main__':
    init_db()
