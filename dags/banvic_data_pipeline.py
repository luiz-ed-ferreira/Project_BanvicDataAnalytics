#Importando as bibliotecas necessárias
from pathlib import Path
from airflow.sdk import dag, task
import pendulum
import sys
sys.path.insert(0, "/opt/airflow/banvic")

#Funções da BanVic
import src.functions as func
import src.preparation_functions as prep
import src.analytics_functions as analytic

#Variavies da BanVic
from src.variables import (
    OLD_DATASET_DIR,
    NEW_DATASET_DIR,
    OUTPUT_FILE,
    DB_CONFIG,
)

#Arquivos esperados em Old_Dataset e New_Dataset
EXPECTED_FILES: list[str] = [
    "agencias.csv",
    "clientes.csv",
    "colaborador_agencia.csv",
    "colaboradores.csv",
    "contas.csv",
    "propostas_credito.csv",
    "transacoes.csv",
]

#Modelo de airflow para pipeline BanVic
    #banvic_data_pipeline.py
    #        │
    #        │  ORQUESTRA
    #        ▼
    #┌─────────────────────────────┐
    #│ check_source_files          │
    #│          ↓                  │
    #│ prepare_and_save_data       │
    #│          ↓                  │
    #│ generate_schema             │
    #│          ↓                  │
    #│ load_to_postgresql          │
    #└─────────────────────────────┘
    #        │
    #        │  UTILIZA
    #        ▼
    #Projeto BanVic / src
    #├── functions.py
    #├── preparation_functions.py
    #├── analytics_functions.py
    #├── monetary_valuations.py
    #└── variables.py

@dag(
    dag_id="banvic_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["banvic", "etl", "data-quality"],
)
def banvic_data_pipeline() -> None:
    """ Orchestrate the BanVic data ingestion and validation pipeline. """

    @task
    def check_source_files() -> None:
        """ Check whether all expected BanVic source files are available. """

        missing_files: list[str] = [
            file_name
            for file_name in EXPECTED_FILES
            if not (OLD_DATASET_DIR / file_name).is_file()
        ]

        if missing_files:
            raise FileNotFoundError(
                f"Missing source files: {', '.join(missing_files)}"
            )

        print(f"All {len(EXPECTED_FILES)} BanVic source files are available.")

    @task
    def prepare_and_save_data() -> None:
        old_datasets = func.load_csv_files(OLD_DATASET_DIR)

        new_datasets = prep.convert_date_columns(old_datasets)
    
        #Identificado no EDA
        anomalous_account_ids: list[int] = [528]

        new_datasets["contas"] = analytic.flag_anomalous_accounts(
            new_datasets["contas"],
            anomalous_account_ids,
        )

        func.save_csv_files(
            new_datasets,
            NEW_DATASET_DIR,
        )

    @task
    def generate_schema() -> None:
        func.generated_schema(
            NEW_DATASET_DIR,
            OUTPUT_FILE,
        )

    @task
    def load_to_postgresql() -> None:
        func.load_all_csvs_to_postgres(
            NEW_DATASET_DIR,
            DB_CONFIG,
        )

    check_files = check_source_files()
    prepare_data = prepare_and_save_data()
    schema = generate_schema()
    load_database = load_to_postgresql()

    check_files >> prepare_data >> schema >> load_database

banvic_data_pipeline()
