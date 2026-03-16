-- GeoAdmin Pro - Migration 005
-- Camadas, geometrias e documentos

CREATE TABLE IF NOT EXISTS camadas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    projeto_id UUID NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    cor_hex TEXT DEFAULT '#FF9500',
    visivel BOOLEAN DEFAULT TRUE,
    bloqueada BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_camadas_projeto_nome ON camadas (projeto_id, nome);

CREATE TABLE IF NOT EXISTS geometrias (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    projeto_id UUID NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('linha', 'poligono', 'perimetro', 'servidao', 'subdivisao')),
    nome TEXT,
    camada TEXT DEFAULT 'DESENHO',
    geometria GEOMETRY(GEOMETRY, 4674) NOT NULL,
    area_m2 NUMERIC(18, 6),
    perimetro_m NUMERIC(18, 6),
    confrontacao_norte TEXT,
    confrontacao_sul TEXT,
    confrontacao_leste TEXT,
    confrontacao_oeste TEXT,
    matricula_origem TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_geometrias_geom ON geometrias USING GIST (geometria);
CREATE INDEX IF NOT EXISTS idx_geometrias_projeto ON geometrias (projeto_id);
CREATE INDEX IF NOT EXISTS idx_geometrias_tipo ON geometrias (tipo);

COMMENT ON TABLE geometrias IS 'Linhas e poligonos desenhados na Vista CAD. Inclui perimetros e subdivisoes.';

CREATE TABLE IF NOT EXISTS documentos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    projeto_id UUID REFERENCES projetos(id) ON DELETE CASCADE,
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN (
        'matricula', 'escritura', 'certidao', 'rg_cpf', 'memorial',
        'planta', 'dxf', 'kml', 'sigef', 'outro'
    )),
    nome_arquivo TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    tamanho_bytes BIGINT,
    mime_type TEXT,
    visivel_cliente BOOLEAN DEFAULT FALSE,
    enviado_por TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_docs_projeto ON documentos (projeto_id);
CREATE INDEX IF NOT EXISTS idx_docs_cliente ON documentos (cliente_id);

COMMENT ON TABLE documentos IS 'Arquivos vinculados a projetos e clientes. Armazenados no Supabase Storage.';
