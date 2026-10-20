# Space Archaeology Intelligence

A full-stack academic platform for satellite data mining and archaeological data warehousing using remote sensing data.

## Overview

This platform provides tools for:
- **Dataset Ingestion**: Upload, validate, and version satellite observation datasets
- **Data Preprocessing**: Clean, transform, and prepare data for analysis
- **Feature Engineering**: Create derived features for ML models
- **Data Mining**: Apply classification, clustering, anomaly detection, and spatial analysis algorithms
- **Model Training**: Train and evaluate ML models for archaeological site prediction
- **Data Warehousing**: Star schema warehouse for analytical queries
- **Interactive Mapping**: Visualize observations and verified archaeological sites
- **Reporting**: Generate comprehensive reports on data quality and analysis results

## Technology Stack

### Backend
- **Python 3.11+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Primary database and data warehouse
- **scikit-learn** - Machine learning
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Leaflet** - Interactive maps
- **React Router** - Navigation
- **Lucide React** - Icons

## Project Structure

```
space-archaeology-intelligence/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── dataset.py
│   │   │   ├── preprocessing.py
│   │   │   ├── mining.py
│   │   │   ├── model.py
│   │   │   ├── etl.py
│   │   │   ├── reference.py
│   │   │   └── warehouse.py
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── dashboard.py
│   │   │   ├── datasets.py
│   │   │   ├── preprocessing.py
│   │   │   ├── features.py
│   │   │   ├── mining.py
│   │   │   ├── models.py
│   │   │   ├── warehouse.py
│   │   │   ├── map.py
│   │   │   └── reports.py
│   │   ├── services/
│   │   │   ├── dataset_service.py
│   │   │   ├── preprocessing_service.py
│   │   │   ├── feature_service.py
│   │   │   ├── mining_service.py
│   │   │   ├── model_service.py
│   │   │   └── warehouse_service.py
│   │   ├── algorithms/
│   │   ├── preprocessing/
│   │   ├── ml/
│   │   ├── etl/
│   │   ├── warehouse/
│   │   ├── geospatial/
│   │   └── utilities/
│   ├── scripts/
│   │   ├── initialize_database.py
│   │   ├── seed_demo_data.py
│   │   ├── run_etl.py
│   │   ├── train_models.py
│   │   └── evaluate_models.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── layouts/
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DatasetExplorer.tsx
│   │   │   ├── PreprocessingStudio.tsx
│   │   │   ├── FeatureEngineering.tsx
│   │   │   ├── MiningLab.tsx
│   │   │   ├── ModelTraining.tsx
│   │   │   ├── ArchaeologicalMap.tsx
│   │   │   ├── WarehouseExplorer.tsx
│   │   │   └── Reports.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── data/
│   ├── raw/
│   ├── processed/
│   ├── sample/
│   └── external/
├── models/
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 1. Clone the Repository

```bash
git clone <repository-url>
cd space-archaeology-intelligence
```

### 2. Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/Mac: source venv/bin/activate
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database migrations
flask --app run.py db init
flask --app run.py db migrate -m "Initial migration"
flask --app run.py db upgrade

# Seed demo data
python scripts\seed_demo_data.py
```

**Note**: The application uses SQLite for development by default. To use PostgreSQL, set the `DATABASE_URL` environment variable in `.env`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev -- --host 127.0.0.1
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

The backend will run on `http://localhost:5000` and the frontend on `http://localhost:3000`.

### Quick Start Commands (Windows)

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
flask --app run.py db init
flask --app run.py db migrate -m "Initial migration"
flask --app run.py db upgrade
python scripts\seed_demo_data.py
python run.py

# Frontend (in new terminal)
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

## Usage

### Initial Workflow

1. **Dashboard**: View summary statistics and charts
2. **Dataset Explorer**: Upload your own CSV dataset or use the demo data
3. **Preprocessing Studio**: Clean and transform data
4. **Feature Engineering**: Create derived features
5. **Mining Lab**: Run data mining algorithms
6. **Model Training**: Train ML models on your data
7. **Archaeological Map**: Visualize observations and sites
8. **Warehouse Explorer**: Explore the data warehouse
9. **Reports**: Generate analysis reports

### Demo Data

The platform includes synthetic demonstration data with:
- 500 satellite observation records
- 5 verified archaeological reference sites (Troy, Knossos, Pyramids of Giza, Petra, Ur)
- Realistic NDVI, NDBI, elevation, soil moisture, surface temperature, and other satellite-derived features
- Archaeological classification labels (verified, candidate, unverified)
- Multiple regions (Aegean, Anatolia, Levant, Egypt, Mesopotamia)

**Note**: This is synthetic data for demonstration and testing purposes only. Do not use for real archaeological analysis.

## API Endpoints

### Health
- `GET /api/v1/health` - Health check

### Dashboard
- `GET /api/v1/dashboard/summary` - Summary statistics
- `GET /api/v1/dashboard/charts` - Chart data

### Datasets
- `GET /api/v1/datasets` - List datasets
- `POST /api/v1/datasets/upload` - Upload dataset
- `GET /api/v1/datasets/{id}/preview` - Preview dataset
- `GET /api/v1/datasets/{id}/profile` - Data profile

### Preprocessing
- `POST /api/v1/preprocessing/preview` - Preview transformations
- `POST /api/v1/preprocessing/run` - Run preprocessing

### Features
- `GET /api/v1/features` - List available features
- `POST /api/v1/features/preview` - Preview features
- `POST /api/v1/features/generate` - Generate features

### Mining
- `GET /api/v1/mining/algorithms` - List algorithms
- `POST /api/v1/mining/run` - Run mining algorithm
- `GET /api/v1/mining/{run_id}/results` - Get results

### Models
- `GET /api/v1/models` - List models
- `POST /api/v1/models/train` - Train model
- `POST /api/v1/models/{id}/predict` - Make predictions
- `GET /api/v1/models/{id}/evaluate` - Evaluate model

### Warehouse
- `GET /api/v1/warehouse/schema` - Get schema
- `GET /api/v1/warehouse/summary` - Get summary
- `GET /api/v1/warehouse/etl/jobs` - List ETL jobs
- `POST /api/v1/warehouse/etl/run` - Run ETL
- `POST /api/v1/warehouse/analytics` - Run analytical query

### Map
- `GET /api/v1/map/observations` - Get observation locations
- `GET /api/v1/map/reference-sites` - Get reference sites

### Reports
- `POST /api/v1/reports/generate` - Generate report

## Data Mining Algorithms

- **Classification**: Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Gaussian Naive Bayes, Gradient Boosting, HistGradientBoosting
- **Regression**: Linear Regression, Ridge Regression, Random Forest Regressor, Gradient Boosting Regressor
- **Clustering**: K-Means, DBSCAN, Agglomerative Clustering, Gaussian Mixture Models
- **Anomaly Detection**: Isolation Forest, Local Outlier Factor, One-Class SVM, Z-Score, IQR
- **Association Rules**: Apriori, FP-Growth
- **Feature Selection**: Correlation Analysis, Variance Threshold, Mutual Information, Recursive Feature Elimination, PCA
- **Spatial Analysis**: Haversine Distance, Nearest Neighbor, Spatial Density, Spatial DBSCAN
- **Temporal Analysis**: Time Series Trend, Seasonal Summary, Change Detection, Rolling Statistics

## Security Notes

- No authentication is currently implemented - this is a demonstration platform
- In production, implement proper authentication and authorization
- Validate all file uploads and sanitize inputs
- Use environment variables for sensitive configuration
- Enable HTTPS in production
- The demo data is synthetic and should not be used for real archaeological analysis

## Testing

```bash
# Backend tests (pytest)
cd backend
pytest tests/

# Frontend build
cd frontend
npm run build
```

## Troubleshooting

### Database Connection Issues
- SQLite is used by default for development
- To use PostgreSQL, set DATABASE_URL in .env
- Verify database exists and user has permissions

### Frontend Build Errors
- Delete node_modules and reinstall: `rm -rf node_modules && npm install` (Linux/Mac) or `Remove-Item -Recurse -Force node_modules; npm install` (Windows)
- Clear Vite cache: `rm -rf .vite` (Linux/Mac) or `Remove-Item -Recurse -Force .vite` (Windows)

### Model Training Errors
- Ensure dataset has required columns
- Check that target column exists in data
- Verify feature columns are numeric
- For classification, ensure target column has sufficient labeled data

### Backend Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` to install all dependencies
- Check that Flask-Migrate is properly initialized

## License

This project is for academic and research purposes.

## Acknowledgments

This platform was developed for space archaeology research using satellite remote sensing data for archaeological site discovery and analysis.
