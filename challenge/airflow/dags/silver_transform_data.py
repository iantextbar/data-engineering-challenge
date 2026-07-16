import os
from datetime import datetime
from typing import Dict, Any

from airflow.sdk import dag, task, Asset
from airflow.exceptions import AirflowException

HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5433")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")
BRONZE_DATASET = Asset(name="postgres_bronze", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/raw_nyc_tlc_data")
SILVER_DATASET = Asset(name="postgres_silver", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/trusted_nyc_tlc_data")

@task
def transform_to_silver():

    from scripts.silver.nyc_data_transformer import NYCTransformer
    
    result = NYCTransformer.transform()

    return result

@task(outlets=[SILVER_DATASET])
def emit_silver(result: Dict[str, Any]):

    if result['statusCode'] == 200:
        return {'status': 'silver_nyc_trips_updated',
                'statusCode': result.get('statusCode')}
    
    raise AirflowException("DAG silver falhou - Gold não será chamada")

@dag(
    dag_id='silver_nyc_processing',
    schedule=[BRONZE_DATASET], 
    start_date=datetime(2026, 1, 1),
    tags=['silver', 'nyc', 'postgres']
)
def silver_processing():
    
    result = transform_to_silver()

    emit_result = emit_silver(result)

    result >> emit_result

silver_processing()

    
