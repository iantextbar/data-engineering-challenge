Separação do DB PostgreSQL do Airflow e o que usaremos para garantir separação de responsabilidades.
Usar LocalExecutor ao invés de CelleryExecutor para reduzir a carga de memória.
Ter um arquivo .sql para automaticamente criar as tabelas quando da subida do container.
Justificar uso do DuckDB para subir os dados e explicar outras estratégias possíveis.
No transformador, explicar o que estamos considerando que é um registro duplicado, limpar valores de distancia negativa e registros sem tempo de chegada. Falar do uso de Data-Aware Scheduling
