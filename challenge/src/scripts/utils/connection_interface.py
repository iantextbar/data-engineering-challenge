import os

import duckdb

# Variaveis globais
HOST = os.environ.get("DW_DB_HOST", "localhost")
PORT = os.environ.get("DW_DB_PORT", "5432")
DBNAME = os.environ.get("DW_DB_NAME", "nyc")
USER = os.environ.get("DW_DB_USER", "user")
PASSWORD = os.environ.get("DW_DB_PASSWORD", "datarisk")
CONNSTRING = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

class ConnectionInterface:

    """
    Interface para execução de queries em DuckDB.
    """

    @staticmethod
    def execute(query: str):
        
        # Conexao e instalacao manual da interacao com Postgres
        con = duckdb.connect()
        con.execute("INSTALL postgres; LOAD postgres;")

        # Conectar com a base
        con.execute(f"ATTACH '{CONNSTRING}' AS pg (TYPE POSTGRES, SCHEMA 'public');")

        # Execute query
        con.execute(query)

        con.close
