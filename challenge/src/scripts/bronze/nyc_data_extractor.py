import logging
from typing import Dict

from src.scripts.utils.connection_interface import ConnectionInterface

# Declarar globals
logger = logging.getLogger(__name__)

class NYCExtractor:

    @staticmethod
    def insert_parquet_file(filename: str) -> Dict[str, int]:

        """
        Le arquivo em parquet diretamente usando funcao do DuckDB e 
        insere todas as colunas para a tabela PostgreSQL da camada bronze
        _______
            Retorna: Dicionario com status da execucao
        """
        
        try:

            logger.info(f"Iniciando extracao do arquivo {filename}")
            
            # Inserir dados
            ConnectionInterface.execute(f"""
                INSERT INTO pg.raw_nyc_tlc_data (
                    VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, 
                    trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, 
                    payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, 
                    improvement_surcharge, total_amount, congestion_surcharge, airport_fee
                ) 
                SELECT 
                    VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, 
                    trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, 
                    payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, 
                    improvement_surcharge, total_amount, congestion_surcharge, airport_fee
                FROM read_parquet('{filename}')
            """)

            logger.info(f"Processo de extracao completo!")

            return {'statusCode': 200}
        
        except Exception as e:

            logger.error(f"ERRO para {filename}: {str(e)}")

            return {'statusCode': 400}
