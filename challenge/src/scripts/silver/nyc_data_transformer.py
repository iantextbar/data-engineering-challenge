import logging

from src.scripts.utils.connection_interface import ConnectionInterface

# Declarar globals
logger = logging.getLogger(__name__)

class NYCTransformer:

    @staticmethod
    def transform():

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

            ConnectionInterface.execute("""
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

            logger.info('Sucesso na transformacao!')

            return {'statusCode': 200}

        except Exception as e:

            logger.error(f'ERRO ao realizar transformação: {str(e)}')

            return {'statusCode': 400}
