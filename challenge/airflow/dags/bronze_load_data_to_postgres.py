import os
from typing import List, Dict, Any
from datetime import datetime

from airflow.sdk import dag, task, Asset

# Declaring global variables
DATA_PATH = "/opt/airflow/data/"
DEFAULT_ARGS = {'owner': 'airflow'}

# Resgatando variaveis ambiente do docker compose
ENV = os.environ.get("DW_DB_HOST", "prod")
HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5433")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")

# Declarando asset
BRONZE_DATASET = Asset(name="postgres_bronze", uri=f"postgres://{HOST}:{PORT}/{DBNAME}/public/raw_nyc_tlc_data")

@task
def get_filename_list() -> List[str]:

    """
    Busca todos os arquivos .parquet.gz
    _______
        Retorna: Lista de str com nomes de arquivos
    """
    
    file_list = [f for f in os.listdir(DATA_PATH) if f.endswith('.parquet.gz')]

    if not file_list:
        raise ValueError(f"Nenhum arquivo .parquet encontrado no diretório: {DATA_PATH}")
    
    if ENV == 'dev':
        return [file_list[0]]

    return file_list

@task
def run_extraction(file_list: List[str]) -> Dict[str, Any]:

    """
    Dada a lista de arquivos, executa o extrator para cada arquivo
    subindo os dados para a tabela raw
    _______
        Retorna: Dicionario com status da execucao
    """

    # Import dentro da funcao para evitar encher a memoria
    # por conta do DAG File Processor
    from scripts.bronze.nyc_data_extractor import NYCExtractor

    extractor = NYCExtractor()

    success_count = 0

    for file_name in file_list:

        file_path = os.path.join(DATA_PATH, file_name)

        result = extractor.insert_parquet_file(file_path)

        if result['statusCode'] == 200:
            success_count += 1

    return {'success_rate': success_count / len(file_list)}

@task(outlets=[BRONZE_DATASET])
def emit_bronze(success_result: Dict[str, Any]):
    return {'status': 'bronze_nyc_trips_updated',
            'success_rate': success_result.get('success_rate')}

@dag(
    dag_id='bronze_nyc_parquet_to_postgres',
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    tags=['bronze', 'nyc', 'postgres']
)
def bronze_extraction():
    
    file_list = get_filename_list()

    success_result = run_extraction(file_list)

    emitted = emit_bronze(success_result)

    file_list >> success_result >> emitted

bronze_extraction()
