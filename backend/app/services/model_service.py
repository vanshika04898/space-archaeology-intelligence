import pandas as pd
import numpy as np
import joblib
import os
import uuid
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from ..extensions import db
from ..models import ModelRegistry, DatasetVersion, Prediction

class ModelService:
    """Service for model training and inference"""
    
    def train_model(self, dataset_version_id, algorithm_name, target_column, feature_columns, parameters, model_name):
        """Train a machine learning model"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        # Validate target column
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        # Validate feature columns
        available_features = [f for f in feature_columns if f in df.columns and f != target_column]
        if not available_features:
            raise ValueError("No valid feature columns available")
        
        # Prepare data
        X = df[available_features]
        y = df[target_column]
        
        # Encode target if categorical
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Select only numeric features
        X_numeric = X.select_dtypes(include=[np.number])
        
        if len(X_numeric.columns) == 0:
            raise ValueError("No numeric features available for training")
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_numeric, y_encoded,
            test_size=parameters.get('test_size', 0.2),
            random_state=parameters.get('random_state', 42),
            stratify=y_encoded
        )
        
        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', self._get_classifier(algorithm_name, parameters))
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = pipeline.predict(X_test)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'n_training_samples': len(X_train),
            'n_test_samples': len(X_test),
            'n_features': len(X_numeric.columns),
            'feature_names': list(X_numeric.columns),
            'target_classes': le.classes_.tolist()
        }
        
        # Add feature importance if available
        if hasattr(pipeline.named_steps['classifier'], 'feature_importances_'):
            metrics['feature_importance'] = dict(zip(
                X_numeric.columns,
                pipeline.named_steps['classifier'].feature_importances_.tolist()
            ))
        
        # Save model
        model_filename = f"{uuid.uuid4().hex}_{algorithm_name}.joblib"
        models_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models')
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, model_filename)
        
        model_artifact = {
            'pipeline': pipeline,
            'label_encoder': le,
            'feature_columns': list(X_numeric.columns),
            'target_column': target_column,
            'algorithm_name': algorithm_name
        }
        
        joblib.dump(model_artifact, model_path)
        
        # Register model in database
        model_version = f"v1.{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        model = ModelRegistry(
            name=model_name,
            algorithm_name=algorithm_name,
            dataset_version_id=dataset_version_id,
            artifact_path=model_path,
            feature_schema_json={'features': list(X_numeric.columns), 'target': target_column},
            preprocessing_config_json={'scaler': 'StandardScaler'},
            metrics_json=metrics,
            model_version=model_version,
            training_timestamp=datetime.utcnow(),
            status='active'
        )
        
        db.session.add(model)
        db.session.commit()
        
        return {
            'model': model.to_dict(),
            'metrics': metrics
        }
    
    def predict(self, model, records):
        """Make predictions using a trained model"""
        # Load model artifact
        model_artifact = joblib.load(model.artifact_path)
        pipeline = model_artifact['pipeline']
        feature_columns = model_artifact['feature_columns']
        le = model_artifact['label_encoder']
        
        # Prepare input data
        df = pd.DataFrame(records)
        
        # Ensure required features are present
        missing_features = set(feature_columns) - set(df.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        X = df[feature_columns].select_dtypes(include=[np.number])
        
        # Make predictions
        predictions_encoded = pipeline.predict(X)
        probabilities = None
        
        if hasattr(pipeline.named_steps['classifier'], 'predict_proba'):
            probabilities = pipeline.predict_proba(X).tolist()
        
        # Decode labels
        predictions = le.inverse_transform(predictions_encoded).tolist()
        
        # Save predictions to database
        for i, (record, pred, prob) in enumerate(zip(records, predictions, probabilities or [None] * len(predictions))):
            prediction = Prediction(
                model_id=model.id,
                record_id=record.get('record_id', f"record_{i}"),
                predicted_class=str(pred),
                predicted_probability=float(prob[1]) if prob and len(prob) > 1 else None,
                prediction_source='api'
            )
            db.session.add(prediction)
        
        db.session.commit()
        
        return {
            'predictions': predictions,
            'probabilities': probabilities,
            'model_id': model.id,
            'model_name': model.name
        }
    
    def evaluate_model(self, model, test_dataset_version_id):
        """Evaluate a model on test data"""
        version = DatasetVersion.query.get_or_404(test_dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        # Load model artifact
        model_artifact = joblib.load(model.artifact_path)
        pipeline = model_artifact['pipeline']
        feature_columns = model_artifact['feature_columns']
        target_column = model_artifact['target_column']
        le = model_artifact['label_encoder']
        
        # Prepare data
        X = df[feature_columns].select_dtypes(include=[np.number])
        y = df[target_column]
        y_encoded = le.transform(y)
        
        # Predict
        y_pred = pipeline.predict(X)
        
        # Calculate metrics
        metrics = {
            'accuracy': float(accuracy_score(y_encoded, y_pred)),
            'precision': float(precision_score(y_encoded, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_encoded, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_encoded, y_pred, average='weighted', zero_division=0)),
            'confusion_matrix': confusion_matrix(y_encoded, y_pred).tolist(),
            'classification_report': classification_report(y_encoded, y_pred, output_dict=True)
        }
        
        return {
            'model_id': model.id,
            'metrics': metrics,
            'test_samples': len(X)
        }
    
    def _load_dataframe(self, file_path):
        """Load dataframe from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            return pd.read_json(file_path)
    
    def _get_classifier(self, algorithm_name, parameters):
        """Get classifier instance based on algorithm name"""
        if algorithm_name == 'logistic_regression':
            from sklearn.linear_model import LogisticRegression
            return LogisticRegression(max_iter=1000, random_state=42)
        elif algorithm_name == 'decision_tree':
            from sklearn.tree import DecisionTreeClassifier
            return DecisionTreeClassifier(random_state=42, max_depth=parameters.get('max_depth', None))
        elif algorithm_name == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        elif algorithm_name == 'knn':
            from sklearn.neighbors import KNeighborsClassifier
            return KNeighborsClassifier(n_neighbors=parameters.get('n_neighbors', 5))
        elif algorithm_name == 'svm':
            from sklearn.svm import SVC
            return SVC(kernel=parameters.get('kernel', 'rbf'), probability=True, random_state=42)
        elif algorithm_name == 'naive_bayes':
            from sklearn.naive_bayes import GaussianNB
            return GaussianNB()
        elif algorithm_name == 'gradient_boosting':
            from sklearn.ensemble import GradientBoostingClassifier
            return GradientBoostingClassifier(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        elif algorithm_name == 'hist_gradient_boosting':
            from sklearn.ensemble import HistGradientBoostingClassifier
            return HistGradientBoostingClassifier(max_iter=parameters.get('max_iter', 100), random_state=42)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
