#Importando as bibliotecas necessárias
import pandas as pd

#----------------------------------------------------------------------------

#Função exclusiva para tratar as colunas com datas dos datasets, convertendo-as para o tipo datetime

def convert_date_columns(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """ Converte as colunas de data dos datasets definidos para o tipo datetime. """

    #As colunas a seguir foram definidas para analise conforme análise da qualidade dos dados e inspeção inicial nos datasets de origem: agencias.csv, clientes.csv, colaboradores.csv, contas.csv, propostas_credito.csv e transacoes.csv
    date_columns: dict[str, list[str]] = {
        "agencias": [
            "data_abertura"
        ],
        "clientes": [
            "data_inclusao",
            "data_nascimento"
        ],
        "colaboradores": [
            "data_nascimento"
        ],
        "contas": [
            "data_abertura",
            "data_ultimo_lancamento"
        ],
        "propostas_credito": [
            "data_entrada_proposta"
        ],
        "transacoes": [
            "data_transacao"
        ]
    }

    for dataset_name, columns in date_columns.items():
        df: pd.DataFrame = datasets[dataset_name]

        for column in columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return datasets

#----------------------------------------------------------------------------