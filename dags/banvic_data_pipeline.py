#Importando as bibliotecas necessárias
import os
import subprocess
import pendulum
from airflow.sdk import dag, task

#Diretorio para volume do airflow
BANVIC_PROJECT_DIR = "/opt/airflow/banvic"

#Função para rodar as tasks do airflow em processos isolados
def run_banvic_task(task_name: str) -> None:
    """Run a BanVic task in an isolated Python process. """

    environment = os.environ.copy()
    environment["PYTHONPATH"] = BANVIC_PROJECT_DIR

    subprocess.run(
        [
            "python",
            "-m",
            "src.airflow_runner",
            task_name,
        ],
        cwd=BANVIC_PROJECT_DIR,
        env=environment,
        check=True,
    )


@dag(
    dag_id="banvic_data_pipeline",
    schedule=None,
    start_date=pendulum.datetime(
        2026, 1, 1, tz="America/Sao_Paulo"
    ),
    catchup=False,
    tags=["banvic", "etl", "data-quality"],
)
def banvic_data_pipeline():

    @task
    def check_source_files():
        run_banvic_task("check_source_files")

    @task
    def prepare_and_save_data():
        run_banvic_task("prepare_and_save_data")

    @task
    def generate_schema():
        run_banvic_task("generate_schema")

    @task
    def load_to_postgresql():
        run_banvic_task("load_to_postgresql")

    (
        check_source_files()
        >> prepare_and_save_data()
        >> generate_schema()
        >> load_to_postgresql()
    )


banvic_data_pipeline()