import logging

from src.scripts.utils.connection_interface import ConnectionInterface

# Declarar globals
logger = logging.getLogger(__name__)

class NYCTransformer:

    @staticmethod
    def create_index():
        """Cria o índice na camada Bronze de forma isolada."""
        logger.info("Garantindo a existência do índice de performance na Bronze...")
        ConnectionInterface.execute("""
            CREATE INDEX IF NOT EXISTS idx_raw_nyc_dedup 
            ON pg.raw_nyc_tlc_data (VendorID, tpep_pickup_datetime, tpep_dropoff_datetime);
        """)
        logger.info("Índice verificado/criado com sucesso!")

    @staticmethod
    def transform_month(mes: int) -> int:
        """Processa a transformação de um único mês por vez."""
        data_inicio = f"2022-{mes:02d}-01 00:00:00"
        data_fim = f"2022-{mes+1:02d}-01 00:00:00" if mes < 12 else "2023-01-01 00:00:00"

        logger.info(f"Iniciando lote Silver para o mês {mes}: {data_inicio} até {data_fim}")

        # Idempotência: Remove dados antigos do mês caso a task precise ser reexecutada
        ConnectionInterface.execute(f"""
            DELETE FROM pg.trusted_nyc_tlc_data 
            WHERE tpep_pickup_datetime >= '{data_inicio}' AND tpep_pickup_datetime < '{data_fim}';
        """)

        # Insere os dados fatiados (O Postgres usa o índice e processa muito mais rápido)
        ConnectionInterface.execute(f"""
            INSERT INTO pg.trusted_nyc_tlc_data (
                VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance
            )
            SELECT DISTINCT ON (VendorID, tpep_pickup_datetime, tpep_dropoff_datetime)
                VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance
            FROM pg.raw_nyc_tlc_data
            WHERE trip_distance > 0 
              AND tpep_pickup_datetime >= '{data_inicio}'
              AND tpep_pickup_datetime < '{data_fim}'
              AND tpep_dropoff_datetime IS NOT NULL
            ORDER BY VendorID, tpep_pickup_datetime, tpep_dropoff_datetime;
        """)

        logger.info(f"Mês {mes} consolidado com sucesso na Silver!")
        return 200
