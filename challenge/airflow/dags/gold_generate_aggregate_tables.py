import os
from datetime import datetime
from typing import Dict, Any

from airflow.sdk import dag, task, Asset

HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5433")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")
SILVER_DATASET = Asset(name="postgres_silver", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/trusted_nyc_tlc_data")

@task
def create_gold_views() -> Dict[str, Any]:

    from scripts.gold.nyc_data_refined_creator import NYCGoldFactory

    result = NYCGoldFactory.create()

    return result

@dag(
    dag_id='gold_nyc_processing',
    schedule=[SILVER_DATASET], 
    start_date=datetime(2026, 1, 1),
    tags=['gold', 'nyc', 'postgres']
)
def gold_processing():
    
    result = create_gold_views()

gold_processing()
