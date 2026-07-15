import os
from datetime import datetime

from airflow.sdk import dag, task, Asset

HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5433")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")
BRONZE_DATASET = Asset(name="postgres_bronze", uri=f'postgres://{HOST}:{PORT}/{DBNAME}/raw_nyc_tlc_data')


@dag(
    dag_id='silver_nyc_processing',
    schedule=[BRONZE_DATASET], 
    start_date=datetime(2026, 1, 1),
    catchup=False
)
def silver_processing():
    # ... suas tasks da camada silver ...
    pass
