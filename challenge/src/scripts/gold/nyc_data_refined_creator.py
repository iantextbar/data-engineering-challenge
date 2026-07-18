import logging

from src.scripts.utils.connection_interface import ConnectionInterface

logger = logging.getLogger(__name__)


class TotalRecordsViewCreator:
    
    @staticmethod
    def create():

        logger.info('Iniciando criação do view de resitros totais')

        try:

            ConnectionInterface.execute(
                """
                CREATE OR REPLACE VIEW pg.v_total_records AS
                SELECT COUNT(*) AS total_records
                FROM pg.trusted_nyc_tlc_data
            """
            )

        except Exception as e:

            logger.error(f'ERRO na criacao da View de total de registros: {str(e)}')

            raise 

class JulyTripsViewCreator:
    
    @staticmethod
    def create():

        logger.info('Iniciando criação do view de total de viagens no dia 17 Julho')
        
        try:

            ConnectionInterface.execute(
                """
                CREATE OR REPLACE VIEW pg.v_july_trips AS
                SELECT COUNT(*) AS total_july_trips
                FROM pg.trusted_nyc_tlc_data
                WHERE CAST(tpep_pickup_datetime AS DATE) = '2022-07-17'
                  AND CAST(tpep_dropoff_datetime AS DATE) = '2022-07-17'
            """
            )

        except Exception as e:

            logger.error(f'ERRO na criacao da View de corridas do dia 17 de Julho: {str(e)}')

            raise 

class LongestTripViewCreator:
    
    @staticmethod
    def create():

        logger.info('Iniciando criação do view de corrida de maior distancia')
        
        try:

            ConnectionInterface.execute(
                """
                CREATE OR REPLACE VIEW pg.v_longest_trip AS
                SELECT tpep_pickup_datetime, trip_distance 
                FROM pg.trusted_nyc_tlc_data 
                ORDER BY trip_distance DESC 
                LIMIT 1
            """
            )

        except Exception as e:

            logger.error(f'ERRO na criacao da View de corrida de maior distancia: {str(e)}')

            raise 

class DescriptiveStatsViewCreator:
    
    @staticmethod
    def create():

        logger.info('Iniciando criação do view de estatísticas descritivas')
        
        try:

            ConnectionInterface.execute(
                """
                CREATE OR REPLACE VIEW pg.v_desc_stats AS
                SELECT MAX(trip_distance) AS max_distance,
                       MIN(trip_distance) AS min_distance,
                       stddev(trip_distance) AS std_deviation,
                       percentile_cont(0.25) WITHIN GROUP (ORDER BY trip_distance) AS q1,
                       percentile_cont(0.50) WITHIN GROUP (ORDER BY trip_distance) AS median,
                       percentile_cont(0.75) WITHIN GROUP (ORDER BY trip_distance) AS q3
                FROM pg.trusted_nyc_tlc_data
            """
            )

        except Exception as e:

            logger.error(f'ERRO na criacao da View de estatísticas descritivas: {str(e)}')

            raise 

class NYCGoldFactory:

    GOLD_VIEW_LIST = [
        TotalRecordsViewCreator,
        JulyTripsViewCreator,
        LongestTripViewCreator,
        DescriptiveStatsViewCreator
    ]

    @classmethod
    def create(cls):

        logger.info("Iniciando a materialização das Views da camada Gold...")
        
        for creator in cls.GOLD_VIEW_LIST:
            creator.create()

        logger.info("Gold materializada")

        return {'statusCode':200}
