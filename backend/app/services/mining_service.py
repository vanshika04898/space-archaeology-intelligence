import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from ..extensions import db
from ..models import DatasetVersion

class MiningService:
    """Service for data mining operations"""
    
    def get_available_algorithms(self):
        """Get list of available data mining algorithms"""
        return {
            'classification': [
                'logistic_regression',
                'decision_tree',
                'random_forest',
                'knn',
                'svm',
                'naive_bayes',
                'gradient_boosting',
                'hist_gradient_boosting'
            ],
            'regression': [
                'linear_regression',
                'ridge_regression',
                'random_forest_regressor',
                'gradient_boosting_regressor'
            ],
            'clustering': [
                'kmeans',
                'dbscan',
                'agglomerative',
                'gaussian_mixture'
            ],
            'association': [
                'apriori',
                'fpgrowth'
            ],
            'anomaly_detection': [
                'isolation_forest',
                'local_outlier_factor',
                'one_class_svm',
                'z_score',
                'iqr'
            ],
            'feature_selection': [
                'correlation_analysis',
                'variance_threshold',
                'mutual_information',
                'recursive_feature_elimination',
                'pca'
            ],
            'spatial': [
                'haversine_distance',
                'nearest_neighbor',
                'spatial_density',
                'spatial_dbscan'
            ],
            'temporal': [
                'time_series_trend',
                'seasonal_summary',
                'change_detection',
                'rolling_statistics'
            ]
        }
    
    def execute_algorithm(self, dataset_version_id, algorithm_name, algorithm_family, parameters, selected_features, run_id):
        """Execute a data mining algorithm"""
        version = DatasetVersion.query.get_or_404(dataset_version_id)
        df = self._load_dataframe(version.file_path)
        
        # Select features if specified
        if selected_features:
            available_features = [f for f in selected_features if f in df.columns]
            df = df[available_features]
        
        # Route to appropriate algorithm handler
        if algorithm_family == 'classification':
            result = self._execute_classification(df, algorithm_name, parameters)
        elif algorithm_family == 'regression':
            result = self._execute_regression(df, algorithm_name, parameters)
        elif algorithm_family == 'clustering':
            result = self._execute_clustering(df, algorithm_name, parameters)
        elif algorithm_family == 'association':
            result = self._execute_association(df, algorithm_name, parameters)
        elif algorithm_family == 'anomaly_detection':
            result = self._execute_anomaly_detection(df, algorithm_name, parameters)
        elif algorithm_family == 'feature_selection':
            result = self._execute_feature_selection(df, algorithm_name, parameters)
        elif algorithm_family == 'spatial':
            result = self._execute_spatial(df, algorithm_name, parameters)
        elif algorithm_family == 'temporal':
            result = self._execute_temporal(df, algorithm_name, parameters)
        else:
            raise ValueError(f"Unknown algorithm family: {algorithm_family}")
        
        # Save results
        result_location = self._save_results(result, run_id)
        
        return {
            'metrics': result.get('metrics', {}),
            'result_location': result_location,
            'algorithm': algorithm_name,
            'family': algorithm_family
        }
    
    def _load_dataframe(self, file_path):
        """Load dataframe from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            return pd.read_json(file_path)
    
    def _execute_classification(self, df, algorithm_name, parameters):
        """Execute classification algorithms"""
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
        from sklearn.preprocessing import LabelEncoder
        
        # Identify target column
        target_col = parameters.get('target_column')
        if not target_col or target_col not in df.columns:
            raise ValueError("Target column must be specified for classification")
        
        # Prepare data
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Encode categorical variables
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Select only numeric features for simplicity
        X_numeric = X.select_dtypes(include=[np.number])
        
        if len(X_numeric.columns) == 0:
            raise ValueError("No numeric features available for classification")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_numeric, y_encoded,
            test_size=parameters.get('test_size', 0.2),
            random_state=parameters.get('random_state', 42),
            stratify=y_encoded
        )
        
        # Import and configure algorithm
        if algorithm_name == 'logistic_regression':
            from sklearn.linear_model import LogisticRegression
            model = LogisticRegression(max_iter=1000, random_state=42)
        elif algorithm_name == 'decision_tree':
            from sklearn.tree import DecisionTreeClassifier
            model = DecisionTreeClassifier(random_state=42, max_depth=parameters.get('max_depth', None))
        elif algorithm_name == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        elif algorithm_name == 'knn':
            from sklearn.neighbors import KNeighborsClassifier
            model = KNeighborsClassifier(n_neighbors=parameters.get('n_neighbors', 5))
        elif algorithm_name == 'svm':
            from sklearn.svm import SVC
            model = SVC(kernel=parameters.get('kernel', 'rbf'), probability=True, random_state=42)
        elif algorithm_name == 'naive_bayes':
            from sklearn.naive_bayes import GaussianNB
            model = GaussianNB()
        elif algorithm_name == 'gradient_boosting':
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        elif algorithm_name == 'hist_gradient_boosting':
            from sklearn.ensemble import HistGradientBoostingClassifier
            model = HistGradientBoostingClassifier(max_iter=parameters.get('max_iter', 100), random_state=42)
        else:
            raise ValueError(f"Unknown classification algorithm: {algorithm_name}")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': {}
        }
        
        # Add feature importance if available
        if hasattr(model, 'feature_importances_'):
            metrics['feature_importance'] = dict(zip(X_numeric.columns, model.feature_importances_.tolist()))
        
        return {
            'metrics': metrics,
            'predictions': y_pred.tolist(),
            'model_type': algorithm_name
        }
    
    def _execute_clustering(self, df, algorithm_name, parameters):
        """Execute clustering algorithms"""
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
        
        # Select numeric features
        X = df.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            raise ValueError("No numeric features available for clustering")
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Import and configure algorithm
        if algorithm_name == 'kmeans':
            from sklearn.cluster import KMeans
            model = KMeans(n_clusters=parameters.get('n_clusters', 3), random_state=42)
            labels = model.fit_predict(X_scaled)
        elif algorithm_name == 'dbscan':
            from sklearn.cluster import DBSCAN
            model = DBSCAN(eps=parameters.get('eps', 0.5), min_samples=parameters.get('min_samples', 5))
            labels = model.fit_predict(X_scaled)
        elif algorithm_name == 'agglomerative':
            from sklearn.cluster import AgglomerativeClustering
            model = AgglomerativeClustering(n_clusters=parameters.get('n_clusters', 3))
            labels = model.fit_predict(X_scaled)
        elif algorithm_name == 'gaussian_mixture':
            from sklearn.mixture import GaussianMixture
            model = GaussianMixture(n_components=parameters.get('n_components', 3), random_state=42)
            labels = model.fit_predict(X_scaled)
        else:
            raise ValueError(f"Unknown clustering algorithm: {algorithm_name}")
        
        # Calculate metrics
        metrics = {
            'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
            'cluster_sizes': pd.Series(labels).value_counts().to_dict()
        }
        
        if len(set(labels)) > 1:
            try:
                metrics['silhouette_score'] = float(silhouette_score(X_scaled, labels))
            except:
                pass
            try:
                metrics['davies_bouldin_score'] = float(davies_bouldin_score(X_scaled, labels))
            except:
                pass
            try:
                metrics['calinski_harabasz_score'] = float(calinski_harabasz_score(X_scaled, labels))
            except:
                pass
        
        return {
            'metrics': metrics,
            'cluster_labels': labels.tolist(),
            'model_type': algorithm_name
        }
    
    def _execute_anomaly_detection(self, df, algorithm_name, parameters):
        """Execute anomaly detection algorithms"""
        from sklearn.preprocessing import StandardScaler
        
        # Select numeric features
        X = df.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            raise ValueError("No numeric features available for anomaly detection")
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        if algorithm_name == 'isolation_forest':
            from sklearn.ensemble import IsolationForest
            model = IsolationForest(contamination=parameters.get('contamination', 0.1), random_state=42)
            anomalies = model.fit_predict(X_scaled)
            anomaly_scores = model.score_samples(X_scaled)
        elif algorithm_name == 'local_outlier_factor':
            from sklearn.neighbors import LocalOutlierFactor
            model = LocalOutlierFactor(n_neighbors=parameters.get('n_neighbors', 20), contamination=parameters.get('contamination', 0.1))
            anomalies = model.fit_predict(X_scaled)
            anomaly_scores = model.negative_outlier_factor_
        elif algorithm_name == 'one_class_svm':
            from sklearn.svm import OneClassSVM
            model = OneClassSVM(nu=parameters.get('nu', 0.1))
            anomalies = model.fit_predict(X_scaled)
            anomaly_scores = model.decision_function(X_scaled)
        elif algorithm_name == 'z_score':
            from scipy import stats
            z_scores = np.abs(stats.zscore(X_scaled))
            anomalies = np.where(z_scores > parameters.get('threshold', 3), -1, 1)[0]
            anomaly_scores = z_scores.mean(axis=1)
        elif algorithm_name == 'iqr':
            Q1 = X_scaled.quantile(0.25)
            Q3 = X_scaled.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            anomalies = np.where(((X_scaled < lower_bound) | (X_scaled > upper_bound)).any(axis=1), -1, 1)
            anomaly_scores = np.sum((X_scaled < lower_bound) | (X_scaled > upper_bound), axis=1)
        else:
            raise ValueError(f"Unknown anomaly detection algorithm: {algorithm_name}")
        
        metrics = {
            'n_anomalies': int(np.sum(anomalies == -1)),
            'anomaly_ratio': float(np.sum(anomalies == -1) / len(anomalies))
        }
        
        return {
            'metrics': metrics,
            'anomaly_labels': anomalies.tolist(),
            'anomaly_scores': anomaly_scores.tolist() if hasattr(anomaly_scores, 'tolist') else list(anomaly_scores),
            'model_type': algorithm_name
        }
    
    def _execute_regression(self, df, algorithm_name, parameters):
        """Execute regression algorithms"""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        target_col = parameters.get('target_column')
        if not target_col or target_col not in df.columns:
            raise ValueError("Target column must be specified for regression")
        
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        X_numeric = X.select_dtypes(include=[np.number])
        
        if len(X_numeric.columns) == 0:
            raise ValueError("No numeric features available for regression")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_numeric, y,
            test_size=parameters.get('test_size', 0.2),
            random_state=parameters.get('random_state', 42)
        )
        
        if algorithm_name == 'linear_regression':
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
        elif algorithm_name == 'ridge_regression':
            from sklearn.linear_model import Ridge
            model = Ridge(alpha=parameters.get('alpha', 1.0))
        elif algorithm_name == 'random_forest_regressor':
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        elif algorithm_name == 'gradient_boosting_regressor':
            from sklearn.ensemble import GradientBoostingRegressor
            model = GradientBoostingRegressor(n_estimators=parameters.get('n_estimators', 100), random_state=42)
        else:
            raise ValueError(f"Unknown regression algorithm: {algorithm_name}")
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        metrics = {
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'r2': float(r2_score(y_test, y_pred))
        }
        
        return {
            'metrics': metrics,
            'predictions': y_pred.tolist(),
            'model_type': algorithm_name
        }
    
    def _execute_association(self, df, algorithm_name, parameters):
        """Execute association rule mining"""
        from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
        
        # Select categorical columns or discretize numeric
        min_support = parameters.get('min_support', 0.1)
        min_confidence = parameters.get('min_confidence', 0.5)
        
        # Discretize numeric columns if needed
        df_encoded = df.copy()
        for col in df.select_dtypes(include=[np.number]).columns:
            df_encoded[col] = pd.qcut(df_encoded[col], q=4, duplicates='drop').astype(str)
        
        # One-hot encode
        df_onehot = pd.get_dummies(df_encoded)
        
        if algorithm_name == 'apriori':
            frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)
        elif algorithm_name == 'fpgrowth':
            frequent_itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
        else:
            raise ValueError(f"Unknown association algorithm: {algorithm_name}")
        
        if len(frequent_itemsets) == 0:
            return {
                'metrics': {'n_rules': 0},
                'rules': [],
                'model_type': algorithm_name
            }
        
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        metrics = {
            'n_rules': len(rules),
            'avg_support': float(rules['support'].mean()),
            'avg_confidence': float(rules['confidence'].mean()),
            'avg_lift': float(rules['lift'].mean())
        }
        
        return {
            'metrics': metrics,
            'rules': rules.to_dict(orient='records'),
            'model_type': algorithm_name
        }
    
    def _execute_feature_selection(self, df, algorithm_name, parameters):
        """Execute feature selection algorithms"""
        from sklearn.feature_selection import VarianceThreshold, mutual_info_classif, RFE
        from sklearn.decomposition import PCA
        from sklearn.ensemble import RandomForestClassifier
        
        X = df.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            raise ValueError("No numeric features available for feature selection")
        
        if algorithm_name == 'variance_threshold':
            selector = VarianceThreshold(threshold=parameters.get('threshold', 0.0))
            X_selected = selector.fit_transform(X)
            selected_features = X.columns[selector.get_support()].tolist()
        elif algorithm_name == 'pca':
            n_components = parameters.get('n_components', min(2, len(X.columns)))
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X)
            selected_features = [f'PC{i+1}' for i in range(n_components)]
            explained_variance = pca.explained_variance_ratio_.tolist()
        elif algorithm_name == 'correlation_analysis':
            corr_matrix = X.corr()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > parameters.get('threshold', 0.8):
                        high_corr_pairs.append({
                            'feature1': corr_matrix.columns[i],
                            'feature2': corr_matrix.columns[j],
                            'correlation': float(corr_matrix.iloc[i, j])
                        })
            return {
                'metrics': {'n_high_correlations': len(high_corr_pairs)},
                'high_correlation_pairs': high_corr_pairs,
                'model_type': algorithm_name
            }
        else:
            raise ValueError(f"Unknown feature selection algorithm: {algorithm_name}")
        
        metrics = {
            'n_original_features': len(X.columns),
            'n_selected_features': len(selected_features),
            'selected_features': selected_features
        }
        
        if algorithm_name == 'pca':
            metrics['explained_variance_ratio'] = explained_variance
        
        return {
            'metrics': metrics,
            'selected_features': selected_features,
            'model_type': algorithm_name
        }
    
    def _execute_spatial(self, df, algorithm_name, parameters):
        """Execute spatial data mining"""
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            raise ValueError("Latitude and longitude columns required for spatial analysis")
        
        if algorithm_name == 'haversine_distance':
            from math import radians, cos, sin, sqrt, asin
            
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371  # Earth radius in km
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                return 2 * R * asin(sqrt(a))
            
            # Calculate distance matrix for first 100 points
            distances = []
            coords = df[['latitude', 'longitude']].head(100).values
            for i in range(len(coords)):
                for j in range(i+1, len(coords)):
                    dist = haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
                    distances.append(dist)
            
            metrics = {
                'n_distances_calculated': len(distances),
                'mean_distance': float(np.mean(distances)) if distances else 0,
                'max_distance': float(np.max(distances)) if distances else 0,
                'min_distance': float(np.min(distances)) if distances else 0
            }
            
            return {
                'metrics': metrics,
                'model_type': algorithm_name
            }
        
        elif algorithm_name == 'spatial_density':
            radius_km = parameters.get('radius_km', 10)
            densities = []
            coords = df[['latitude', 'longitude']].values
            
            for coord in coords:
                lat_diff = (coords[:, 0] - coord[0]).abs()
                lon_diff = (coords[:, 1] - coord[1]).abs()
                count = ((lat_diff * 111 <= radius_km) & (lon_diff * 111 <= radius_km)).sum()
                densities.append(count - 1)
            
            metrics = {
                'mean_density': float(np.mean(densities)),
                'max_density': int(np.max(densities)),
                'min_density': int(np.min(densities))
            }
            
            return {
                'metrics': metrics,
                'densities': densities,
                'model_type': algorithm_name
            }
        
        else:
            raise ValueError(f"Unknown spatial algorithm: {algorithm_name}")
    
    def _execute_temporal(self, df, algorithm_name, parameters):
        """Execute temporal data mining"""
        if 'observation_date' not in df.columns:
            raise ValueError("observation_date column required for temporal analysis")
        
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        
        if algorithm_name == 'time_series_trend':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            trends = {}
            for col in numeric_cols:
                if col in df.columns:
                    # Simple linear trend
                    df_sorted = df.sort_values('observation_date')
                    x = np.arange(len(df_sorted))
                    y = df_sorted[col].dropna().values
                    if len(y) > 1:
                        slope = np.polyfit(x[:len(y)], y, 1)[0]
                        trends[col] = float(slope)
            
            return {
                'metrics': {'trends': trends},
                'model_type': algorithm_name
            }
        
        elif algorithm_name == 'seasonal_summary':
            df['month'] = df['observation_date'].dt.month
            df['season'] = df['month'].apply(lambda x: 'spring' if x in [3,4,5] else 'summer' if x in [6,7,8] else 'fall' if x in [9,10,11] else 'winter')
            
            seasonal_stats = df.groupby('season').agg({
                col: ['mean', 'std'] for col in df.select_dtypes(include=[np.number]).columns
            }).to_dict()
            
            return {
                'metrics': {'seasonal_statistics': seasonal_stats},
                'model_type': algorithm_name
            }
        
        else:
            raise ValueError(f"Unknown temporal algorithm: {algorithm_name}")
    
    def _save_results(self, result, run_id):
        """Save mining results to file"""
        results_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'mining_results')
        os.makedirs(results_dir, exist_ok=True)
        
        result_file = os.path.join(results_dir, f'run_{run_id}_{datetime.utcnow().timestamp()}.json')
        with open(result_file, 'w') as f:
            json.dump(result, f, default=str)
        
        return result_file
    
    def load_results(self, result_location):
        """Load mining results from file"""
        if not os.path.exists(result_location):
            return {'error': 'Result file not found'}
        
        with open(result_location, 'r') as f:
            return json.load(f)
