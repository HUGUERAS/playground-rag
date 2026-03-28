-- GeoAdmin Pro - Migration 004
-- Tabela de pontos

CREATE TABLE IF NOT EXISTS pontos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    projeto_id UUID NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    descricao TEXT,
    codigo TEXT,
    coordenada GEOMETRY(POINT, 4674) NOT NULL,
    altitude_m NUMERIC(10, 4),
    separacao_geoidal_m NUMERIC(8, 4),
    qualidade_fix INTEGER DEFAULT 0 CHECK (qualidade_fix IN (0, 1, 2, 4, 5)),
    hdop NUMERIC(5, 2),
    num_satelites INTEGER,
    num_amostras INTEGER DEFAULT 1,
    camada TEXT DEFAULT 'PONTOS',
    coletado_em TIMESTAMPTZ DEFAULT NOW(),
    operador TEXT,
    receptor_gnss TEXT DEFAULT 'CHC i73+',
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    sincronizado BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pontos_coordenada ON pontos USING GIST (coordenada);
CREATE INDEX IF NOT EXISTS idx_pontos_projeto ON pontos (projeto_id);
CREATE INDEX IF NOT EXISTS idx_pontos_camada ON pontos (camada);
CREATE INDEX IF NOT EXISTS idx_pontos_sync ON pontos (sincronizado) WHERE sincronizado = FALSE;

COMMENT ON TABLE pontos IS 'Pontos coletados em campo com receptor GNSS. Nucleo do sistema.';
COMMENT ON COLUMN pontos.coordenada IS 'Geometria POINT em SRID 4674 (SIRGAS 2000).';
COMMENT ON COLUMN pontos.qualidade_fix IS '4=RTK Fix (centimetrico). Usar apenas qualidade >= 4 para levantamentos oficiais.';
COMMENT ON COLUMN pontos.sincronizado IS 'FALSE = coletado offline, ainda nao enviado ao servidor.';
