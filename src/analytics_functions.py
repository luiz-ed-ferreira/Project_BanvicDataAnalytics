#Importando as bibliotecas necessárias
import pandas as pd

#----------------------------------------------------------------------------

#Função que analisa quantidade de transações por tipo
def analyze_transaction_volume_by_type(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """ Analisa o volume de transações por tipo de operação. """

    transaction_volume: pd.DataFrame = (
        transactions_df
        .groupby("nome_transacao")
        .agg(
            transaction_count=("cod_transacao", "count")
        )
        .reset_index()
        .sort_values(
            "transaction_count",
            ascending=False
        )
    )

    return transaction_volume

#----------------------------------------------------------------------------

#Função que classifica clientes ativos (pelo menos 1 transação) e clientes inativos (sem transações) em 2022
def analyze_customer_activity_2022(customers_df: pd.DataFrame,transactions_df: pd.DataFrame,accounts_df: pd.DataFrame) -> pd.DataFrame:
    """ Classifica os clientes como ativos ou sem transações em 2022 (pedido para analise do time comercial). """

    active_customers = (
        transactions_df[
            transactions_df["data_transacao"]
            .dt.tz_localize(None)
            .dt.year
            .eq(2022)
        ]
        .merge(
            accounts_df[["num_conta", "cod_cliente"]],
            on="num_conta",
            how="left"
        )["cod_cliente"]
        .dropna()
        .unique()
    )

    activity = customers_df[["cod_cliente"]].copy()

    activity["activity_status"] = activity["cod_cliente"].isin(
        active_customers
    ).map({
        True: "Active",
        False: "No transactions"
    })

    result = (
        activity
        .groupby("activity_status")
        .agg(
            customer_count=("cod_cliente", "count")
        )
        .reset_index()
    )

    result["percentage"] = round((
        result["customer_count"]
        / result["customer_count"].sum()
        * 100
    ),2)

    return result

#----------------------------------------------------------------------------

#Função analisa a tendência de inatividade anual dos clientes
def analyze_customer_activity_by_year(customers_df: pd.DataFrame, transactions_df: pd.DataFrame,accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
        Analisa a atividade anual dos clientes.
        Classifica cada cliente como ativo ou sem transações em cada ano disponível na base de transações.
    """
    transaction_data = (
        transactions_df
        .assign(
            transaction_year=lambda df: (
                df["data_transacao"]
                .dt.tz_localize(None)
                .dt.year
            )
        )
        .merge(
            accounts_df[["num_conta", "cod_cliente"]],
            on="num_conta",
            how="left"
        )
        [["transaction_year", "cod_cliente"]]
        .dropna()
        .drop_duplicates()
    )

    years = sorted(transaction_data["transaction_year"].unique())

    customer_year = (
        pd.MultiIndex.from_product(
            [customers_df["cod_cliente"], years],
            names=["cod_cliente", "transaction_year"]
        )
        .to_frame(index=False)
    )

    customer_year["is_active"] = (
        customer_year
        .merge(
            transaction_data.assign(is_active=True),
            on=["cod_cliente", "transaction_year"],
            how="left"
        )["is_active"]
        .fillna(False)
    )

    activity_by_year = (
        customer_year
        .assign(
            activity_status=lambda df: df["is_active"].map({
                True: "Active",
                False: "No transactions"
            })
        )
        .groupby(["transaction_year", "activity_status"])
        .agg(
            customer_count=("cod_cliente", "count")
        )
        .reset_index()
    )

    activity_by_year["percentage"] = round((
        activity_by_year["customer_count"]
        / len(customers_df)
        * 100
    ),2)

    return activity_by_year

#----------------------------------------------------------------------------

#Função que analisa o crescimento acumulado de contas abertas ao longo dos anos, segmentado por tipo de agência e composição entre contas digitais e físicas.
def analyze_cumulative_account_growth(accounts_df: pd.DataFrame, agencies_df: pd.DataFrame) -> pd.DataFrame:
    """Analisa o crescimento acumulado de contas abertas ao longo dos anos, segmentado por tipo de agência e tipo de conta. """

    account_growth: pd.DataFrame = (
        accounts_df
        .merge(
            agencies_df[
                ["cod_agencia", "tipo_agencia"]
            ],
            on="cod_agencia",
            how="left"
        )
        .assign(
            opening_year=lambda df: (
                df["data_abertura"]
                .dt.tz_localize(None)
                .dt.year
            )
        )
        .groupby(
            ["opening_year", "tipo_agencia", "tipo_conta"]
        )
        .agg(
            new_accounts=("num_conta", "count")
        )
        .reset_index()
        .sort_values(
            ["tipo_agencia", "opening_year", "tipo_conta"]
        )
    )

    #Calcula o número acumulado de contas por tipo de conta e agência
    account_growth["cumulative_accounts"] = (
        account_growth
        .groupby(
            ["tipo_agencia", "tipo_conta"]
        )["new_accounts"]
        .cumsum()
    )

    return account_growth

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
