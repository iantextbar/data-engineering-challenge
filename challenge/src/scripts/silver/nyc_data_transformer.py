import os
import logging

import duckdb

# Declarar globals
logger = logging.getLogger(__name__)

class NYCTransformer:

    def __init__(self):

        # Garantia da seguranca das credenciais 
        # (para o exemplo em particular fallbacks explicitas) pois dados nao sao sensiveis
        self.host = os.environ.get("DW_DB_HOST", "localhost")
        self.port = os.environ.get("DW_DB_PORT", "5432")
        self.dbname = os.environ.get("DW_DB_NAME", "nyc")
        self.user = os.environ.get("DW_DB_USER", "user")
        self.password = os.environ.get("DW_DB_PASSWORD", "datarisk")

        self.conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    def transform(self):

        """
        Com base nos registro da raw_nyc_tlc_data, realiza deduplicacao, particionando os 
        dados por corridas com o mesmo VendorID, tempo de inicio e final e pegando apenas o
        primeiro registro da particao. Elimina registros errados, com distancia de corrida
        menor ou igual a zero e sem valores de tempo de inicio e fim.
        _______
            Retorna: Dicionario com status da execucao
        """

        logger.info(f"Iniciando extracao do arquivo")

        try:
            # Conexao e instalacao manual da interacao com Postgres
            con = duckdb.connect()
            con.execute("INSTALL postgres; LOAD postgres;")
            # Conectar com a base
            con.execute(f"ATTACH '{self.conn_string}' AS pg (TYPE POSTGRES, SCHEMA 'public');")

            con.execute("""
            INSERT INTO pg.trusted_nyc_tlc_data (
                    VendorID,
                    tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    trip_distance
                )
                SELECT
                    VendorID,
                    tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    trip_distance
                FROM (
                    SELECT 
                        tpep_pickup_datetime,
                        tpep_dropoff_datetime,
                        trip_distance,
                        VendorID, 
                        ROW_NUMBER() OVER (
                            PARTITION BY VendorID, tpep_pickup_datetime, tpep_dropoff_datetime 
                            ORDER BY tpep_pickup_datetime
                        ) as row_num
                    FROM pg.raw_nyc_tlc_data
                    WHERE trip_distance > 0 
                      AND tpep_pickup_datetime IS NOT NULL
                      AND tpep_dropoff_datetime IS NOT NULL
                )
                WHERE row_num = 1
            """)

            con.close()

            logger.info('Sucesso na transformacao!')

            return {'statusCode': 200}

        except Exception as e:

            logger.error(f'ERRO ao realizar transformação: {str(e)}')
            
            return {'statusCode': 400}
