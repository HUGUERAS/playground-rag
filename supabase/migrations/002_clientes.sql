-- GeoAdmin Pro - Migration 002
-- Tabela de clientes

CREATE TABLE IF NOT EXISTS clientes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(nome) >= 2),
    cpf_cnpj TEXT UNIQUE,
    telefone TEXT,
    email TEXT,
    magic_link_token UUID,
    magic_link_expira TIMESTAMPTZ,
    municipio TEXT,
    estado TEXT DEFAULT 'GO' CHECK (length(estado) = 2),
    cep TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes (nome);

COMMENT ON TABLE clientes IS 'Proprietarios e contratantes dos servicos topograficos.';
COMMENT ON COLUMN clientes.magic_link_token IS 'Token unico para acesso ao portal do cliente sem senha.';
