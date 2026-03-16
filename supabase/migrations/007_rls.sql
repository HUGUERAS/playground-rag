-- GeoAdmin Pro - Migration 007
-- Row Level Security

ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE projetos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pontos ENABLE ROW LEVEL SECURITY;
ALTER TABLE camadas ENABLE ROW LEVEL SECURITY;
ALTER TABLE geometrias ENABLE ROW LEVEL SECURITY;
ALTER TABLE documentos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS topografo_acesso_total ON clientes;
CREATE POLICY topografo_acesso_total ON clientes
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS topografo_acesso_total ON projetos;
CREATE POLICY topografo_acesso_total ON projetos
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS topografo_acesso_total ON pontos;
CREATE POLICY topografo_acesso_total ON pontos
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS topografo_acesso_total ON camadas;
CREATE POLICY topografo_acesso_total ON camadas
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS topografo_acesso_total ON geometrias;
CREATE POLICY topografo_acesso_total ON geometrias
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS topografo_acesso_total ON documentos;
CREATE POLICY topografo_acesso_total ON documentos
    FOR ALL TO authenticated
    USING (true)
    WITH CHECK (true);
