#Importando as bibliotecas necessárias
import json
from pathlib import Path

#----------------------------------------------------------------------------
#Adaptando variables.py para funcionar tanto pelo notebooks quanto pelo airflow em container
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#Definindo o diretório onde os arquivos CSVs estão localizados, onde serão salvos e o nome do arquivo de saída do schema SQL
OLD_DATASET_DIR = PROJECT_ROOT / "Old_Dataset"
NEW_DATASET_DIR = PROJECT_ROOT / "New_Dataset"
OUTPUT_FILE = PROJECT_ROOT / "schema" / "schema_banvic.sql"

#----------------------------------------------------------------------------

#Banco de dados associado ao PostgreSQL (Configurado para conexão com localhost)
DB_CONFIG_FILE = PROJECT_ROOT / "config" / "db_config.json"
with DB_CONFIG_FILE.open("r", encoding="utf-8") as file:
    config = json.load(file)

#Arquivo de configuração do banco de dados PostgreSQL não será carregado no GitHub por questões de segurança
DB_CONFIG = {
    "host": config["host"],
    "port": config["port"],
    "database": config["database"],
    "user": config["user"],
    "password": config["password"]
}

#----------------------------------------------------------------------------