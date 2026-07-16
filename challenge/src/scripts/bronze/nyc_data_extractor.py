import os
import logging
from typing import Dict

import duckdb

# Declarar globals
logger = logging.getLogger(__name__)

class NYCExtractor:

    def __init__(self):

        # Garantia da seguranca das credenciais 
        # (para o exemplo em particular fallbacks explicitas) pois dados nao sao sensiveis
        self.host = os.environ.get("DW_DB_HOST", "localhost")
        self.port = os.environ.get("DW_DB_PORT", "5432")
        self.dbname = os.environ.get("DW_DB_NAME", "nyc")
        self.user = os.environ.get("DW_DB_USER", "user")
        self.password = os.environ.get("DW_DB_PASSWORD", "datarisk")

        self.conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    def insert_parquet_file(self, filename: str) -> Dict[str, int]:

        """
        Le arquivo em parquet diretamente usando funcao do DuckDB e 
        insere todas as colunas para a tabela PostgreSQL da camada bronze
        _______
            Retorna: Dicionario com status da execucao
        """
        
        try:

            logger.info(f"Iniciando extracao do arquivo {filename}")

            # Conexao e instalacao manual da interacao com Postgres
            con = duckdb.connect()
            con.execute("INSTALL postgres; LOAD postgres;")

            # Conectar com a base
            con.execute(f"ATTACH '{self.conn_string}' AS pg (TYPE POSTGRES, SCHEMA 'public');")
            
            # Inserir dados
            con.execute(f"""
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

            con.close()

            logger.info(f"Processo de extracao completo!")

            return {'statusCode': 200}
        except Exception as e:
            logger.error(f"ERRO para {filename}: {str(e)}")
            return {'statusCode': 400}
