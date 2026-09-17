#Importando as bibliotecas necessárias
import pandas as pd

#----------------------------------------------------------------------------

#Função para analisar a relação de clientes e suas contas bancárias
def analyze_customer_accounts(customers_df: pd.DataFrame, accounts_df: pd.DataFrame) -> dict[str, int | float | pd.DataFrame]:
    """ Analisa a relação entre clientes e contas bancárias. """

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

#Função para identificar quais contas bancárias são anômalas com base em uma lista de identificadores fornecida
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
        .resample("ME") #Mensal
        .agg(
            transaction_count=("cod_transacao", "count"),
            total_transaction_value=("valor_transacao", "sum"),
            average_transaction_value=("valor_transacao", "mean")
        )
        .reset_index()
    )

    return monthly_transactions

#----------------------------------------------------------------------------

#Função para analisar a relação entre clientes, agências e transações de acordo com o periodo mensal
def analyze_transaction_profile(transactions_df: pd.DataFrame, accounts_df: pd.DataFrame, customers_df: pd.DataFrame, agencies_df: pd.DataFrame) -> pd.DataFrame:
    """
        Analisa a evolução das transações considerando o tipo de cliente,
        o tipo de agência e o tipo de transação.
    """

    transaction_profile: pd.DataFrame = (
        transactions_df
        .merge(
            accounts_df[
                ["num_conta", "cod_cliente", "cod_agencia"]
            ],
            on="num_conta",
            how="left"
        )
        .merge(
            customers_df[
                ["cod_cliente", "tipo_cliente"]
            ],
            on="cod_cliente",
            how="left"
        )
        .merge(
            agencies_df[
                ["cod_agencia", "tipo_agencia"]
            ],
            on="cod_agencia",
            how="left"
        )
        .assign(
            transaction_month=lambda df: (
                df["data_transacao"]
                .dt.tz_localize(None)
                .dt.to_period("M")
            )
        )
        .groupby(
            [
                "transaction_month",
                "tipo_cliente",
                "tipo_agencia",
                "nome_transacao"
            ]
        )
        .agg(
            transaction_count=("cod_transacao", "count"),
            total_transaction_value=("valor_transacao", "sum")
        )
        .reset_index()
    )

    return transaction_profile

#----------------------------------------------------------------------------

#Função para analisar evolução mensal das transações por agência fisica ou digital
def prepare_channel_evolution(transaction_profile_df: pd.DataFrame) -> pd.DataFrame:
    """ Analisa a evolução mensal das transações por tipo de agência. """

    channel_evolution: pd.DataFrame = (
        transaction_profile_df
        .groupby(
            [
                "transaction_month",
                "tipo_agencia"
            ]
        )
        .agg(
            transaction_count=("transaction_count", "sum")
        )
        .reset_index()
        .sort_values("transaction_month")
    )

    return channel_evolution

#----------------------------------------------------------------------------

#Função para analisar a evolução mensal do PIX em comparação com as outras transações
def prepare_pix_evolution(transaction_profile_df: pd.DataFrame) -> pd.DataFrame:
    """ 
        Prepara a evolução mensal das transações PIX versus demais tipos de transação. 
        Detalhamento das transações via PIX obtidas após analisar os valores da coluna nome_transacao no dataset transacao.csv.
    """
    
    pix_transaction_types: list[str] = [
        "Pix - Realizado",
        "Pix - Recebido",
        "Pix Saque"
    ]

    pix_evolution: pd.DataFrame = (
        transaction_profile_df
        .assign(
            transaction_group=lambda df: df["nome_transacao"].apply(
                lambda transaction_type: (
                    "PIX"
                    if transaction_type in pix_transaction_types
                    else "Others"
                )
            )
        )
        .groupby(
            [
                "transaction_month",
                "transaction_group"
            ]
        )
        .agg(
            transaction_count=("transaction_count", "sum")
        )
        .reset_index()
        .sort_values("transaction_month")
    )

    return pix_evolution

#----------------------------------------------------------------------------
