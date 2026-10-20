"""
Train machine learning models on labeled data.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Dataset, DatasetVersion
from app.services.model_service import ModelService

def train_models():
    """Train models on available labeled data"""
    app = create_app('development')
    
    with app.app_context():
        # Get dataset with labeled data
        dataset = Dataset.query.filter_by(name='Demo Satellite Archaeological Data').first()
        if not dataset:
            print("No demo dataset found. Please seed demo data first.")
            return
        
        version = DatasetVersion.query.filter_by(dataset_id=dataset.id).first()
        if not version:
            print("No dataset version found.")
            return
        
        print(f"Training models on dataset: {dataset.name}")
        
        service = ModelService()
        
        # Train a Random Forest classifier
        try:
            print("\nTraining Random Forest classifier...")
            result = service.train_model(
                dataset_version_id=version.id,
                algorithm_name='random_forest',
                target_column='archaeological_status',
                feature_columns=['ndvi', 'ndbi', 'elevation', 'soil_moisture', 'surface_temperature', 'distance_from_water'],
                parameters={'n_estimators': 100, 'random_state': 42, 'test_size': 0.2},
                model_name='Archaeological_Status_Classifier'
            )
            print(f"  - Model ID: {result['model']['id']}")
            print(f"  - Accuracy: {result['metrics']['accuracy']:.4f}")
            print(f"  - F1 Score: {result['metrics']['f1_score']:.4f}")
        except Exception as e:
            print(f"  - Error training Random Forest: {e}")
        
        # Train a Decision Tree classifier
        try:
            print("\nTraining Decision Tree classifier...")
            result = service.train_model(
                dataset_version_id=version.id,
                algorithm_name='decision_tree',
                target_column='site_type',
                feature_columns=['ndvi', 'ndbi', 'elevation', 'soil_moisture'],
                parameters={'max_depth': 10, 'random_state': 42, 'test_size': 0.2},
                model_name='Site_Type_Classifier'
            )
            print(f"  - Model ID: {result['model']['id']}")
            print(f"  - Accuracy: {result['metrics']['accuracy']:.4f}")
            print(f"  - F1 Score: {result['metrics']['f1_score']:.4f}")
        except Exception as e:
            print(f"  - Error training Decision Tree: {e}")
        
        print("\nModel training complete.")

if __name__ == '__main__':
    train_models()
