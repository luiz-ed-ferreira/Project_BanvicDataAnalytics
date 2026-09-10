#Importando as bibliotecas necessárias
import json

#----------------------------------------------------------------------------

#Definindo o diretório onde os arquivos CSVs estão localizados, onde serão salvos e o nome do arquivo de saída do schema
OLD_DATASER_DIR = "Old_Dataset"
NEW_DATASER_DIR = "New_Dataset"
OUTPUT_FILE = "Schema/schema_banvic.sql"

#----------------------------------------------------------------------------

#Banco de dados associado ao PostgreSQL (Configurado para conexão com localhost)
with open("Config/db_config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

#Arquivo de configuração do banco de dados PostgreSQL não será carregado no GitHub por questões de segurança
#ip route | grep default > para verificar qual é o IP do host
DB_CONFIG = {
    "host": config["host"],
    "port": config["port"],
    "database": config["database"],
    "user": config["user"],
    "password": config["password"]
}