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

#Importando as bibliotecas necessárias
import argparse

#Funções da BanVic
from src import analytics_functions as analytic
from src import functions as func
from src import preparation_functions as prep

#Variavies da BanVic
from src.variables import (
    OLD_DATASET_DIR,
    NEW_DATASET_DIR,
    OUTPUT_FILE,
    DB_CONFIG,
)

#Arquivos esperados em Old_Dataset e New_Dataset
EXPECTED_FILES = [
    "agencias.csv",
    "clientes.csv",
    "colaborador_agencia.csv",
    "colaboradores.csv",
    "contas.csv",
    "propostas_credito.csv",
    "transacoes.csv",
]


def check_source_files() -> None:
    """ Check whether all expected BanVic source files are available. """

    missing_files = [
        filename
        for filename in EXPECTED_FILES
        if not (OLD_DATASET_DIR / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing source files: {', '.join(missing_files)}"
        )

    print("All source files are available.")


def prepare_and_save_data() -> None:
    old_datasets = func.load_csv_files(OLD_DATASET_DIR)
    new_datasets = prep.convert_date_columns(old_datasets)

    #Identificado no EDA
    new_datasets["contas"] = analytic.flag_anomalous_accounts(
        new_datasets["contas"],
        [528],
    )

    func.save_csv_files(new_datasets, NEW_DATASET_DIR)


def generate_schema() -> None:
    func.generated_schema(NEW_DATASET_DIR, OUTPUT_FILE)


def load_to_postgresql() -> None:
    func.load_all_csvs_to_postgres(NEW_DATASET_DIR, DB_CONFIG)


TASKS = {
    "check_source_files": check_source_files,
    "prepare_and_save_data": prepare_and_save_data,
    "generate_schema": generate_schema,
    "load_to_postgresql": load_to_postgresql,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS.keys())
    args = parser.parse_args()

    TASKS[args.task]()


if __name__ == "__main__":
    main()