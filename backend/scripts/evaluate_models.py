"""
Evaluate trained models and generate reports.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import ModelRegistry, DatasetVersion

def evaluate_models():
    """Evaluate all trained models"""
    app = create_app('development')
    
    with app.app_context():
        models = ModelRegistry.query.filter_by(status='active').all()
        
        if not models:
            print("No trained models found. Train models first using train_models.py")
            return
        
        print(f"Found {len(models)} trained models\n")
        
        for model in models:
            print(f"Model: {model.name}")
            print(f"  Algorithm: {model.algorithm_name}")
            print(f"  Version: {model.model_version}")
            print(f"  Training date: {model.training_timestamp}")
            print(f"  Metrics:")
            
            if model.metrics_json:
                for key, value in model.metrics_json.items():
                    if isinstance(value, (int, float)):
                        print(f"    {key}: {value:.4f}")
                    elif key not in ['confusion_matrix', 'feature_importance']:
                        print(f"    {key}: {value}")
            
            print()

if __name__ == '__main__':
    evaluate_models()
