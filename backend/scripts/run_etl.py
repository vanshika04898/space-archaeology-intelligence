"""
Run ETL job to load data into the data warehouse.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Dataset
from app.services.warehouse_service import WarehouseService

def run_etl(dataset_id=None):
    """Run ETL job for a specific dataset"""
    app = create_app('development')
    
    with app.app_context():
        if dataset_id is None:
            # Use the first available dataset
            dataset = Dataset.query.first()
            if not dataset:
                print("No datasets found. Please seed demo data first.")
                return
            dataset_id = dataset.id
        
        print(f"Running ETL job for dataset {dataset_id}...")
        
        service = WarehouseService()
        result = service.run_etl(dataset_id, 'full_load')
        
        print(f"\nETL job completed:")
        print(f"  - Job ID: {result['job_id']}")
        print(f"  - Status: {result['status']}")
        print(f"  - Rows read: {result['rows_read']}")
        print(f"  - Rows inserted: {result['rows_inserted']}")
        print(f"  - Rows rejected: {result['rows_rejected']}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run ETL job')
    parser.add_argument('--dataset-id', type=int, help='Dataset ID to process')
    args = parser.parse_args()
    
    run_etl(args.dataset_id)
