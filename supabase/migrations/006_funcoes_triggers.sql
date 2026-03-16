-- GeoAdmin Pro - Migration 006
-- Funcoes e triggers

CREATE OR REPLACE FUNCTION utm_srid_por_zona(zona TEXT)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE UPPER(COALESCE(zona, '23S'))
        WHEN '18S' THEN 31978
        WHEN '19S' THEN 31979
        WHEN '20S' THEN 31980
        WHEN '21S' THEN 31981
        WHEN '22S' THEN 31982
        WHEN '23S' THEN 31983
        WHEN '24S' THEN 31984
        WHEN '25S' THEN 31985
        ELSE 31983
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_projetos_updated ON projetos;
CREATE TRIGGER trg_projetos_updated
    BEFORE UPDATE ON projetos
    FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

DROP TRIGGER IF EXISTS trg_geometrias_updated ON geometrias;
CREATE TRIGGER trg_geometrias_updated
    BEFORE UPDATE ON geometrias
    FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

CREATE OR REPLACE FUNCTION criar_camadas_padrao()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO camadas (projeto_id, nome, cor_hex) VALUES
        (NEW.id, 'PONTOS', '#FF9500'),
        (NEW.id, 'PERIMETRO', '#FF0000'),
        (NEW.id, 'FRONTEIRA', '#FF6600'),
        (NEW.id, 'SERVIDAO', '#0066FF'),
        (NEW.id, 'DESENHO', '#FFFFFF'),
        (NEW.id, 'TEXTOS', '#FFFFFF')
    ON CONFLICT (projeto_id, nome) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_projetos_camadas ON projetos;
CREATE TRIGGER trg_projetos_camadas
    AFTER INSERT ON projetos
    FOR EACH ROW EXECUTE FUNCTION criar_camadas_padrao();

CREATE OR REPLACE FUNCTION calcular_area_perimetro()
RETURNS TRIGGER AS $$
DECLARE
    projeto_zona TEXT;
    projeto_srid INTEGER;
BEGIN
    SELECT zona_utm INTO projeto_zona
    FROM projetos
    WHERE id = NEW.projeto_id;

    projeto_srid := utm_srid_por_zona(projeto_zona);

    IF ST_GeometryType(NEW.geometria) IN ('ST_Polygon', 'ST_MultiPolygon') THEN
        NEW.area_m2 = ST_Area(ST_Transform(NEW.geometria, projeto_srid));
        NEW.perimetro_m = ST_Perimeter(ST_Transform(NEW.geometria, projeto_srid));
    ELSIF ST_GeometryType(NEW.geometria) IN ('ST_LineString', 'ST_MultiLineString') THEN
        NEW.area_m2 = NULL;
        NEW.perimetro_m = ST_Length(ST_Transform(NEW.geometria, projeto_srid));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_geometrias_area ON geometrias;
CREATE TRIGGER trg_geometrias_area
    BEFORE INSERT OR UPDATE ON geometrias
    FOR EACH ROW EXECUTE FUNCTION calcular_area_perimetro();
