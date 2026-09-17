#Importando as bibliotecas necessárias
import pandas as pd
import os
import csv
import psycopg2
from datetime import datetime

#----------------------------------------------------------------------------

#Função para apresentar as colunas dos arquivos CSVs em uma pasta especifica
def show_columns(data_path: str) -> None:
    """ Lê todos os arquivos CSVs de uma pasta e apresenta as colunas existentes em cada arquivo. """

    files = sorted(
        file for file in os.listdir(data_path)
        if file.lower().endswith(".csv")
    )

    if not files:
        print(f"Nenhum arquivo CSV encontrado na pasta '{data_path}'.")
        return

    print(f"Arquivos encontrados: {len(files)}\n")

    for file in files:
        path = os.path.join(data_path, file)

        df = pd.read_csv(path)

        print("=" * 60)
        print(f"Arquivo: {file}")
        print(f"Quantidade de colunas: {len(df.columns)}")
        print("-" * 60)
        
        for col in df.columns:
            print(f"- {col}")

        print()

#----------------------------------------------------------------------------

#Função para carregar os arquivos CSVs para identificar a quantidade de linhas e colunas
def load_csv_files(data_path: str) -> dict[str, pd.DataFrame]:
    """
        Lê todos os arquivos CSVs de um diretório especificado e retorne um dicionário contendo os dataframes correspondentes.
        Auxilia na identificação da quantidade de linhas e colunas de cada arquivo CSV. 
    """

    datasets: dict[str, pd.DataFrame] = {}

    csv_files: list[str] = sorted(
        file_name
        for file_name in os.listdir(data_path)
        if file_name.lower().endswith(".csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in directory: '{data_path}'"
        )

    for file_name in csv_files:
        file_path: str = os.path.join(data_path, file_name)
        dataset_name: str = os.path.splitext(file_name)[0]

        datasets[dataset_name] = pd.read_csv(file_path)

    return datasets

#----------------------------------------------------------------------------

#Função para inspecionar os tipos de dados de todos os dataframes carregados no dicionário
def inspect_data_types(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """ Inspeciona os tipos de dados de todos os dataframes carregados no dicionário. """

    data_types: dict[str, pd.DataFrame] = {}

    for dataset_name, df in datasets.items():
        data_types[dataset_name] = pd.DataFrame({
            "column": df.columns,
            "data_type": df.dtypes.astype(str).values
        })

    return data_types

#----------------------------------------------------------------------------

#Função para identificar valores nulos de todos os dataframes carregados no dicionário
def inspect_missing_values(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
        Identifica valores nulos de todos os dataframes carregados no dicionário. 
        Retorna um dicionário com dataframes contendo a contagem e a porcentagem de valores nulos por coluna para cada tabela.
    """

    missing_values: dict[str, pd.DataFrame] = {}

    for dataset_name, df in datasets.items():

        missing_count: pd.Series = df.isna().sum()

        missing_percentage: pd.Series = (
            df.isna().mean() * 100
        )

        result: pd.DataFrame = pd.DataFrame({
            "column": df.columns,
            "missing_count": missing_count.values,
            "missing_percentage": missing_percentage.values
        })

        result = result.sort_values(
            by="missing_count",
            ascending=False
        ).reset_index(drop=True)

        missing_values[dataset_name] = result

    return missing_values

#----------------------------------------------------------------------------

#Função para identificar valores duplicados de todos os dataframes carregados no dicionário (linha a linha)
def inspect_duplicate_rows(datasets: dict[str, pd.DataFrame]) -> dict[str, dict[str, int]]:
    """ Identifica registros completamente duplicados de todos os dataframes carregados no dicionário (linha a linha). """

    duplicate_summary: dict[str, dict[str, int]] = {}

    for dataset_name, df in datasets.items():

        total_rows: int = len(df)
        duplicate_rows: int = int(df.duplicated().sum()) #Registro inteiro
        unique_rows: int = total_rows - duplicate_rows

        duplicate_summary[dataset_name] = {
            "total_rows": total_rows,
            "duplicate_rows": duplicate_rows,
            "unique_rows": unique_rows
        }

    return duplicate_summary

#----------------------------------------------------------------------------

#Função para identificar valores duplicados em todas as tabelas com base em chaves primarias (PKs)
def inspect_key_uniqueness(datasets: dict[str, pd.DataFrame], key_mapping: dict[str, list[str]]) -> dict[str, dict[str, int | bool]]:
    """ 
        Valida se as chaves primarias (PKs) de todos os dataframes carregados no dicionário são únicas. 
        As colunas definidas como PKs precisam ser adicionadas no key_mapping.
    """

    uniqueness_summary: dict[str, dict[str, int | bool]] = {}

    for dataset_name, key_columns in key_mapping.items():

        df: pd.DataFrame = datasets[dataset_name]

        total_rows: int = len(df)

        unique_keys: int = int(
            df[key_columns].drop_duplicates().shape[0]
        )

        duplicated_keys: int = int(
            df.duplicated(
                subset=key_columns,
                keep=False
            ).sum()
        )

        is_unique: bool = duplicated_keys == 0

        uniqueness_summary[dataset_name] = {
            "total_rows": total_rows,
            "unique_keys": unique_keys,
            "duplicated_keys": duplicated_keys,
            "is_unique": is_unique
        }

    return uniqueness_summary

#----------------------------------------------------------------------------

#Função para salvar todos os dataframes carregados no dicionário tratados em arquivos CSVs
def save_csv_files(datasets: dict[str, pd.DataFrame],output_path: str) -> None:
    """
        Salva os dataframes tratados em arquivos CSVs.
        O nome de cada arquivo será baseado na chave correspondente de todos os dataframes carregados no dicionário.
    """

    os.makedirs(output_path, exist_ok=True)

    for dataset_name, df in datasets.items():
        file_path: str = os.path.join(
            output_path,
            f"{dataset_name}.csv"
        )

        df.to_csv(
            file_path,
            index=False
        )

#----------------------------------------------------------------------------

#Função para identificar as colunas que são identificadores (id), que devem ser tratados como TEXT
def id_type_column(column_name: str) -> bool:
    """ Verifica se a coluna representa um identificador (id) para ser tratada separadamente como TEXT no schema SQL. """

    #Informações obtidas da função show_columns, que mostra as colunas dos arquivos CSVs
    column_name = column_name.strip().lower()
    return (
        column_name == "id"
        or column_name.startswith("cod_")
        or column_name.startswith("num_")
        or column_name == "cpfcnpj"
        or column_name == "cep"
        or column_name == "cpf"
        or column_name == "cnpj"
    )

#----------------------------------------------------------------------------

#Função para inferir o tipo de dados de cada coluna com base nos valores encontrados nos datasets CSVs
def infer_type(column_name: str, values: list) -> str:
    """ Infere o tipo de dado SQL de acordo com o que o PostgreSQL aceita no schema com base nos valores encontrados de todos os dataframes carregados no dicionário. """
    
    values = [value.strip() for value in values if value.strip()]

    #Colunas de ids serão sempre tratados como TEXT
    if id_type_column(column_name):
        return "TEXT"

    values = [
        value.strip()
        for value in values
        if value.strip() != ""
    ]

    #TEXT
    if not values:
        return "TEXT"

    #INTEGER
    try:
        for value in values:
            int(value)
        return "INTEGER"
    except ValueError:
        pass

    #NUMERIC
    try:
        for value in values:
            float(value)
        return "NUMERIC"
    except ValueError:
        pass

    #DATE / TIMESTAMP
    parsed_values: list[datetime] = []

    for value in values:
        normalized_value: str = value.strip()

        #Trata valores terminados em UTC.
        if normalized_value.endswith(" UTC"):
            normalized_value = normalized_value[:-4] + "+00:00"

        try:
            parsed_value: datetime = datetime.fromisoformat(
                normalized_value
            )
            parsed_values.append(parsed_value)

        except ValueError:
            parsed_values = []
            break

    if parsed_values:
        has_time: bool = any(
            value.hour != 0
            or value.minute != 0
            or value.second != 0
            or value.microsecond != 0
            or value.tzinfo is not None
            for value in parsed_values
        )

        if has_time:
            return "TIMESTAMP"

        return "DATE"

    return "TEXT"

#----------------------------------------------------------------------------

#Função para tratar os nomes de tabelas e colunas para o PostgreSQL
def created_table_name(filename: str) -> str:
    """ Utiliza o nome do arquivo CSV como nome da tabela SQL. """
    
    table_name = os.path.splitext(filename)[0]

    return table_name.lower()

#----------------------------------------------------------------------------

#Função para tratar os nomes de tabelas e colunas para o PostgreSQL
def created_column_name(column: str) -> str:
    """ Normaliza o nome das colunas para PostgreSQL de acordo com o nome das colunas de todos os dataframes do dicionário carregado. """

    #Tratamento de possiveis espaços e caracteres especiais no nome da coluna
    column = column.strip()
    column = column.replace(" ", "_")
    column = column.replace("-", "_")

    return column.lower()

#----------------------------------------------------------------------------

#Função para gerar o schema SQL a partir dos arquivos CSVs
def generated_schema(data_path: str, output_file: str) -> None:
    """ Gera o schema SQL a partir dos arquivos CSVs no diretório especificado. """

    sql_statements = []
    files = sorted(os.listdir(data_path))

    for filename in files:
        #Apenas selecionar arquivos .csv no diretório especificado
        if not filename.lower().endswith(".csv"):
            continue

        filepath = os.path.join(data_path, filename)
        table_name = created_table_name(filename)
    
        print(f"Processando: {filename}")

        with open(filepath, "r", encoding="utf-8-sig", newline="") as csvfile:

            reader = csv.reader(csvfile)
            header = next(reader)
            rows = list(reader)
            columns = list(zip(*rows)) if rows else [[] for _ in header]
            column_definitions = []

            for column_name, values in zip(header, columns):
                original_column_name = column_name #Para verifcar as colunas ids
                column_name = created_column_name(column_name)
                data_type = infer_type(original_column_name, values)
                column_definitions.append(
                    f'    "{column_name}" {data_type}'
                )

            create_table = (
                f'CREATE TABLE "{table_name}" (\n'
                + ",\n".join(column_definitions)
                + "\n);\n"
            )

            sql_statements.append(create_table)

    with open(output_file, "w", encoding="utf-8") as sqlfile:
        sqlfile.write(
            "-- Schema gerado automaticamente a partir do arquivo CSVs tratados na pasta \"New_Dataset\"\n\n"
        )
        sqlfile.write(
            "\n".join(sql_statements)
        )

#----------------------------------------------------------------------------

#Função para tratar nomes de tabelas e colunas para o PostgreSQL sendo as mesmas usadas para gerar o schema SQL a partir dos arquivos CSVs
def created_table_name(filename: str) -> str:
    """ Utiliza o nome do arquivo CSV como nome da tabela SQL. """
    table_name = os.path.splitext(filename)[0]

    return table_name.lower()

#----------------------------------------------------------------------------

#Função para tratar nomes de tabelas e colunas para o PostgreSQL sendo as mesmas usadas para gerar o schema SQL a partir dos arquivos CSVs
def created_column_name(column: str) -> str:
    """ Normaliza o nome das colunas para PostgreSQL. """

    #Tratamento de possiveis espaços e caracteres especiais no nome da coluna
    column = column.strip()
    column = column.replace(" ", "_")
    column = column.replace("-", "_")

    return column.lower()

#----------------------------------------------------------------------------

#Função para inserir os dados dos arquivos CSVs no PostgreSQL
def load_csv_to_postgres(connection, filepath: str):
    """ Insere os dados de um arquivo CSV em sua respectiva tabela PostgreSQL presente no arquivo schemas.sql. """

    filename = os.path.basename(filepath)
    table_name = created_table_name(filename)

    print(f"Carregando: {filename}")

    #Cursor para consultar os tipos das colunas
    cur = connection.cursor()

    with open(
        filepath,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        columns = [
            created_column_name(column)
            for column in header
        ]
        column_list = ", ".join(
            f'"{column}"'
            for column in columns
        )
        placeholders = ", ".join(
            ["%s"] * len(columns)
        )

        #Consulta os tipos das colunas da tabela no PostgreSQL para tratar valores nulos (SQL)
        cur.execute("""
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table_name,))

        column_types = {
            column_name: data_type
            for column_name, data_type in cur.fetchall()
        }

        #Ação de INSERT no PostgreSQL (SQL)
        insert_query = f"""
            INSERT INTO "{table_name}"
            ({column_list})
            VALUES ({placeholders})
        """

        #INSERT SQL e tratamento de valores nulos
        for row in reader:
            new_row = []
            for column, value in zip(columns, row):
                column_type = column_types.get(column)

                #Se o valor estiver vazio e a coluna for DATE, TIMESTAMP ou INTEGER são os mais afetados, então o valor serão tratados como nulos (SQL)
                if value == "" and column_type in (
                    "date",
                    "timestamp without time zone",
                    "timestamp with time zone",
                    "integer"
                ):
                    value = None
                new_row.append(value)
            cur.execute(
                insert_query,
                new_row
            )

        connection.commit()
        cur.close()
    print(f"  {filename} inserido com sucesso!")

#----------------------------------------------------------------------------

#Função para chamar todos os arquivos CSVs e a partir da função load_csv_to_postgres inserir no PostgreSQL
def load_all_csvs_to_postgres(data_path: str, db_config: dict) -> None:
    """ Carrega todos os arquivos CSV do diretório informado para o banco de dados PostgreSQL. """

    connection = psycopg2.connect(**db_config)

    #Busca apenas arquivos CSVs no diretório informado e chama a função load_csv_to_postgres para cada arquivo encontrado
    try:
        files = sorted(os.listdir(data_path))
        for filename in files:
            if not filename.lower().endswith(".csv"):
                continue
            filepath = os.path.join(
                data_path,
                filename
            )
            load_csv_to_postgres(
                connection,
                filepath
            )
    except Exception as error:
        connection.rollback()
        print(
            f"Erro durante o carregamento: {error}")
        raise

    finally:
        connection.close()

#----------------------------------------------------------------------------
