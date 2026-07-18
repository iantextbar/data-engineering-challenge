import os
from datetime import datetime
from typing import List

from airflow.sdk import dag, task, Asset
from airflow.exceptions import AirflowException

HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5432")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")
BRONZE_DATASET = Asset(name="postgres_bronze", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/raw_nyc_tlc_data")
SILVER_DATASET = Asset(name="postgres_silver", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/trusted_nyc_tlc_data")

@task
def prepare_bronze_index():
    """Task Upstream: Executa a criação do índice antes de fatiar os meses."""
    from scripts.silver.nyc_data_transformer import NYCTransformer
    NYCTransformer.create_index()

@task
def get_months_list() -> List[int]:
    """Retorna a lista dos meses de janeiro a dezembro."""
    return list(range(1, 13))

@task(max_active_tis_per_dag=1)
def transform_to_silver_chunk(mes: int) -> int:
    """Task Mapeada: Processa um único mês de forma isolada."""
    from scripts.silver.nyc_data_transformer import NYCTransformer
    try:
        status_code = NYCTransformer.transform_month(mes)
        return status_code
    except Exception as e:
        raise AirflowException(f"Falha catastrófica no lote do mês {mes}: {str(e)}")

@task(outlets=[SILVER_DATASET])
def emit_silver(results: List[int]):
    """Task Downstream: Só roda se TODAS as tasks mapeadas retornarem sucesso."""
    return {'status': 'silver_nyc_trips_updated'}

@dag(
    dag_id='silver_nyc_processing',
    schedule=[BRONZE_DATASET], 
    start_date=datetime(2026, 1, 1),
    tags=['silver', 'nyc', 'postgres'],
    max_active_runs=1
)
def silver_processing():
    
    index_ready = prepare_bronze_index()
    
    months = get_months_list()
    
    chunk_results = transform_to_silver_chunk.expand(mes=months)
    
    emitted = emit_silver(chunk_results)

    index_ready >> months >> chunk_results >> emitted

silver_processing()

    
