import logging

from src.scripts.utils.connection_interface import ConnectionInterface

logger = logging.getLogger(__name__)

# Qual o total de registros na tabela final?
# Qual o total de viagens iniciadas e finalizadas no dia 17 de junho?
# Qual foi o dia da viagem mais longa percorrida?
# Qual a média, o desvio padrão, o mínimo, o máximo e os quartis da distribuição de distância percorrida nas viagens totais?


class TotalRecordsViewCreator:
    
    @staticmethod
    def create():

        try:
            ConnectionInterface.execute()
        except Exception as e:

            logger.error(f'ERRO na criacao da View de total de registros: {str(e)}')

            raise

class JulyTripsViewCreator:
    pass

class LongestTripViewCreator:
    pass

class DescriptiveStatsViewCreator:
    pass

class NYCGoldCreator:

    def __init__(self):
        pass

    def create():
        pass
