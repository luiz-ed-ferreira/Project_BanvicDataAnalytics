-- Schema gerado automaticamente

CREATE TABLE "agencias" (
    "cod_agencia" TEXT,
    "nome" TEXT,
    "endereco" TEXT,
    "cidade" TEXT,
    "uf" TEXT,
    "data_abertura" DATE,
    "tipo_agencia" TEXT
);

CREATE TABLE "clientes" (
    "cod_cliente" TEXT,
    "primeiro_nome" TEXT,
    "ultimo_nome" TEXT,
    "email" TEXT,
    "tipo_cliente" TEXT,
    "data_inclusao" TEXT,
    "cpfcnpj" TEXT,
    "data_nascimento" DATE,
    "endereco" TEXT,
    "cep" TEXT
);

CREATE TABLE "colaborador_agencia" (
    "cod_colaborador" TEXT,
    "cod_agencia" TEXT
);

CREATE TABLE "colaboradores" (
    "cod_colaborador" TEXT,
    "primeiro_nome" TEXT,
    "ultimo_nome" TEXT,
    "email" TEXT,
    "cpf" TEXT,
    "data_nascimento" DATE,
    "endereco" TEXT,
    "cep" TEXT
);

CREATE TABLE "contas" (
    "num_conta" TEXT,
    "cod_cliente" TEXT,
    "cod_agencia" TEXT,
    "cod_colaborador" TEXT,
    "tipo_conta" TEXT,
    "data_abertura" TEXT,
    "saldo_total" NUMERIC,
    "saldo_disponivel" NUMERIC,
    "data_ultimo_lancamento" TEXT
);

CREATE TABLE "propostas_credito" (
    "cod_proposta" TEXT,
    "cod_cliente" TEXT,
    "cod_colaborador" TEXT,
    "data_entrada_proposta" TEXT,
    "taxa_juros_mensal" NUMERIC,
    "valor_proposta" NUMERIC,
    "valor_financiamento" NUMERIC,
    "valor_entrada" NUMERIC,
    "valor_prestacao" NUMERIC,
    "quantidade_parcelas" INTEGER,
    "carencia" INTEGER,
    "status_proposta" TEXT
);

CREATE TABLE "transacoes" (
    "cod_transacao" TEXT,
    "num_conta" TEXT,
    "data_transacao" TEXT,
    "nome_transacao" TEXT,
    "valor_transacao" NUMERIC
);
