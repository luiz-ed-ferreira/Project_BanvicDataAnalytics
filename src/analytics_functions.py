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

#Função para identificar quais contas bancárias são anomalas com base em uma lista de identificadores fornecida.
def flag_anomalous_accounts(accounts_df: pd.DataFrame,anomalous_account_ids: list[int]) -> pd.DataFrame:
    """
        Adiciona uma flag identificando contas classificadas como anômalas.
        Retorna um dataFrame contendo a coluna 'anomalia', com True para contas anômalas e False para as demais.
    """

    accounts_df = accounts_df.copy()

    accounts_df["anomalia"] = (
        accounts_df["num_conta"].isin(anomalous_account_ids)
    )

    return accounts_df

#----------------------------------------------------------------------------

#Função para analisar a evolução das transações bancárias ao longo do periodo mensal
def analyze_transaction_evolution(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
        Analisa a evolução mensal das transações bancárias.
        A análise calcula a quantidade de transações, o valor total transacionado e o ticket médio por mês.
    """

    monthly_transactions: pd.DataFrame = (
        transactions_df
        .set_index("data_transacao")
        .resample("ME")
        .agg(
            transaction_count=("cod_transacao", "count"),
            total_transaction_value=("valor_transacao", "sum"),
            average_transaction_value=("valor_transacao", "mean")
        )
        .reset_index()
    )

    return monthly_transactions