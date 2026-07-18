# Pipeline de Engenharia de Dados: NYC TLC Case

O maior desafio deste projeto foi a **severa restrição de hardware**. O ambiente de desenvolvimento rodou sobre uma instância WSL limitada a **4GB de RAM** (em uma máquina física de 8GB). Aumentar a alocação do Docker para 6GB colocaria em risco a estabilidade do sistema operacional hospedeiro.

Por conta disso, cada decisão arquitetural — da escolha das ferramentas ao design das DAGs — foi desenhada estrategicamente para **minimizar o consumo de memória e evitar falhas por OOM (Out of Memory)**.

---

## 1. Setup da Infraestrutura e Ambiente

* **Otimização do Executor:** Substituí o `CeleryExecutor` pelo `LocalExecutor`. Isso eliminou a necessidade de subir serviços auxiliares de mensageria (como Redis ou RabbitMQ), liberando preciosos megabytes de RAM para o core do pipeline.
* **Isolamento do Data Warehouse:** Provisionei um container PostgreSQL dedicado (`postgres_dw`) independente do banco de metadados do Airflow, garantindo o isolamento completo das responsabilidades.
* **Ajuste de Timeouts:** O tempo limite das tarefas (*DAG Timeout*) foi expandido de 30 para 120 segundos, prevenindo que a lentidão inicial na leitura de pacotes pesados causasse quedas prematuras.
* **Carga Declarativa e Dockerização:** Centralizei a instalação de dependências via Dockerfile e estruturei scripts SQL em `challenge/airflow/init-scripts/` para garantir que as tabelas das camadas *Raw* e *Trusted* fossem provisionadas automaticamente na inicialização dos containers.

---

## 2. Camada Bronze: Fase de Extração

O core do extrator (`challenge/src/scripts/bronze/nyc_data_extractor.py`) utiliza o **DuckDB** devido à sua capacidade nativa, extremamente veloz e eficiente, de ler arquivos Parquet compactados (`.parquet.gz`) via streaming direto para o PostgreSQL.

> **Decisão de Arquitetura:** Embora abordagens com PyArrow ou inserções em lote (*batches*) via SQLAlchemy fossem viáveis, o DuckDB ofereceu a melhor eficiência de memória com menor complexidade de código.

### Orquestração e Gerenciamento de Memória

Para evitar o acúmulo de lixo na memória do processo Python, a DAG utiliza **Mapeamento Dinâmico de Tarefas** (`.expand()`).

* O Airflow isola a carga de cada um dos 12 meses em uma sub-task independente.
* A configuração `max_active_tis_per_dag=1` garante que apenas um mês seja processado por vez. Assim que o mês finaliza, o container libera 100% da RAM antes de iniciar o próximo.

Todo o fluxo foi construído utilizando **Data-Aware Scheduling**, fazendo com que o término de uma camada dispare a próxima automaticamente através da atualização de `Assets`.

---

## 3. Camada Silver: Fase de Transformação

Desenvolvida em `challenge/src/scripts/silver/nyc_data_transformer.py`, esta fase limpa e consolida os dados através de regras de negócio estritas:

* **Seleção de Atributos:** Filtramos e mantivemos apenas as colunas estritamente necessárias para as análises do cliente, reduzindo o tamanho da tabela no disco e na memória.
* **Deduplicação Inteligente:** Removemos registros duplicados aplicando a cláusula `DISTINCT ON` combinada com chaves de unicidade (identificador do motorista e horários exatos de início/fim da corrida).
* **Sanitização:** Expurgamos registros corrompidos com distâncias negativas ou iguais a zero (erros latentes de imputação na origem).

### Estratégia de Execução

Para suportar o pesado processo de ordenação do `DISTINCT ON` dentro do Postgres sem estourar o limite de 4GB, implementamos duas defesas:

1. **Indexação Prévia:** Um método isolado cria um índice B-Tree na tabela Raw antes das transformações.
2. **Processamento Fatiado e Idempotente:** A DAG processa a transformação mês a mês em loops controlados, limpando o destino antes de reinserir os dados (`DELETE + INSERT`), o que blinda o pipeline contra duplicidade em caso de reexecuções.

---

## 4. Camada Gold: Fase de Refino

Na camada Gold, focamos em **extensibilidade e manutenabilidade** aplicando o padrão de projeto **Factory (Padrão Criacional)**.

Cada indicador ou agrupamento analítico possui sua própria classe isolada, facilitando a inclusão de novas métricas no futuro sem impactar o código existente (seguindo o princípio Open/Closed do **SOLID**).

As queries são encapsuladas e enviadas ao banco via `CALL postgres_execute()`, permitindo que o Postgres materialize as Views localmente em alta performance e evitando erros de referências cruzadas entre bancos.

---

## 5. Resultados Analíticos (Respostas)

Abaixo estão os resultados consolidados obtidos diretamente através das Views materializadas na Camada Gold:

### Q1: Total de Registros na Base Consolidada

| Métrica | Total de Registros |
| --- | --- |
| **`total_records`** | 38.844.799 |

### Q2: Total de Viagens Registradas no Dia 17 de Julho

| Métrica | Total de Viagens (17/07) |
| --- | --- |
| **`total_july_trips`** | 88.324 |

### Q3: Corrida com a Maior Distância Registrada

| Data/Hora da Viagem (`tpep_pickup_datetime`) | Distância da Corrida (`trip_distance`) |
| --- | --- |
| 28/10/2022 às 05:19:00 | **389.678,46** |

### Q4: Estatísticas Descritivas da Distância das Corridas

| Métrica | Valor (Milhas) |
| --- | --- |
| **Distância Máxima** (`max_distance`) | 389.678,46 |
| **Distância Mínima** (`min_distance`) | 0,01 |
| **Desvio Padrão** (`std_deviation`) | 602,43 |
| **1º Quartil (Q1)** (`q1`) | 1,14 |
| **Mediana (Q2)** (`median`) | 1,91 |
| **3º Quartil (Q3)** (`q3`) | 3,60 |
