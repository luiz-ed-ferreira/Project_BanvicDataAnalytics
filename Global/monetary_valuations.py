#Importando as bibliotecas necessárias
import pandas as pd
from datetime import datetime

#----------------------------------------------------------------------------

#Função exclusiva para inspecionar os valores das propostas de crédito do dataset 'propostas_credito.csv'
def inspect_credit_proposals(df: pd.DataFrame) -> dict[str, int]:
    """ Identifica possíveis inconsistências nos valores das propostas de crédito do dataset 'propostas_credito.csv'. """

    #As colunas a seguir foram prdefinidas para analise conforme inspeção inicial no dataset de origem: propostas_credito.csv
    validation_summary: dict[str, int] = {
        "entry_greater_than_proposal": int(
            (df["valor_entrada"] > df["valor_proposta"]).sum()
        ),
        "financing_equal_than_proposal_plus_entry": int(
            (
                df["valor_financiamento"].round(2)
                ==
                (
                    df["valor_proposta"] + df["valor_entrada"]
                ).round(2)
            ).sum()
        ),
        "non_positive_installment": int(
            (df["valor_prestacao"] <= 0).sum()
        ),
        "non_positive_installments_quantity": int(
            (df["quantidade_parcelas"] <= 0).sum()
        ),
        "negative_interest_rate": int(
            (df["taxa_juros_mensal"] < 0).sum()
        )
    }

    return validation_summary
#----------------------------------------------------------------------------

#Função exclusiva para inspecionar os valores das transaçõesdo dataset 'transacoes.csv'
def inspect_transaction_values(df: pd.DataFrame) -> dict[str, int]:
    """ Identifica possíveis inconsistências nos valores das transações do dataset 'transacoes.csv'. """

    #As colunas a seguir foram prdefinidas para analise conforme inspeção inicial no dataset de origem: transacoes.csv
    validation_summary: dict[str, int] = {
        "negative_values": int(
            (df["valor_transacao"] < 0).sum()
        ),
        "zero_values": int(
            (df["valor_transacao"] == 0).sum()
        ),
        "positive_values": int(
            (df["valor_transacao"] > 0).sum()
        )
    }

    return validation_summary
#----------------------------------------------------------------------------
