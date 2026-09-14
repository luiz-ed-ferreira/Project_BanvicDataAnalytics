#Importando as bibliotecas necessárias
import pandas as pd

#----------------------------------------------------------------------------

#Função para analisar a relação de clientes e suas contas bancárias
def analyze_customer_accounts(customers_df: pd.DataFrame, accounts_df: pd.DataFrame) -> dict[str, int | float | pd.DataFrame]:
    """
        Analisa a relação entre clientes e contas bancárias.

        A análise responde às seguintes perguntas:
        1. Quantos clientes possuem pelo menos uma conta?
        2. Quantos clientes possuem mais de uma conta?
        3. Existem contas sem cliente correspondente?

    """

    customer_ids: pd.Series = customers_df["cod_cliente"]
    account_customer_ids: pd.Series = accounts_df["cod_cliente"]

    accounts_per_customer: pd.Series = (
        accounts_df
        .groupby("cod_cliente")
        .size()
        .rename("account_count")
    )

    customers_with_accounts: int = int(
        accounts_per_customer.index.isin(customer_ids).sum()
    )

    customers_with_multiple_accounts: int = int(
        (accounts_per_customer > 1).sum()
    )

    #Observação: ~ é o operador de negação (NOT) em pandas, utilizado para inverter a condição de filtragem.
    unmatched_account_indices: pd.Index = accounts_df.index[
        ~account_customer_ids.isin(customer_ids)
    ]

    accounts_without_customer: int = len(unmatched_account_indices)

    return {
        "total_customers": len(customers_df),
        "total_accounts": len(accounts_df),
        "customers_with_accounts": customers_with_accounts,
        "customers_with_multiple_accounts": customers_with_multiple_accounts,
        "accounts_without_customer": accounts_without_customer,
        "unmatched_account_indices": unmatched_account_indices
    }

#----------------------------------------------------------------------------
