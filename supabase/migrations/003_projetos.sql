-- GeoAdmin Pro - Migration 003
-- Tabela de projetos

CREATE TABLE IF NOT EXISTS projetos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id) ON DELETE RESTRICT,
    nome TEXT NOT NULL,
    numero_job TEXT UNIQUE,
    descricao TEXT,
    municipio TEXT,
    estado TEXT DEFAULT 'GO',
    matricula TEXT,
    comarca TEXT,
    zona_utm TEXT DEFAULT '23S',
    srid INTEGER DEFAULT 4674,
    status TEXT DEFAULT 'medicao'
        CHECK (status IN ('medicao', 'montagem', 'protocolado', 'aprovado', 'finalizado')),
    data_medicao DATE,
    data_protocolo DATE,
    data_aprovacao DATE,
    data_entrega DATE,
    prazo_estimado DATE,
    valor_servico NUMERIC(10, 2),
    valor_pago NUMERIC(10, 2) DEFAULT 0,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_projetos_cliente ON projetos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_projetos_status ON projetos (status);
CREATE INDEX IF NOT EXISTS idx_projetos_numero ON projetos (numero_job);

COMMENT ON TABLE projetos IS 'Projetos e levantamentos topograficos. Cada projeto pertence a um cliente.';
COMMENT ON COLUMN projetos.numero_job IS 'Numero no formato do LandStar 7: AAAAMMDD + sequencial.';
COMMENT ON COLUMN projetos.srid IS 'SRID do sistema de referencia. 4674 = SIRGAS 2000 geografico.';
