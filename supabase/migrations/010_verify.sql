-- GeoAdmin Pro - Migration 010
-- Verificacao final

SELECT
    pt.nome,
    ST_Y(pt.coordenada) AS latitude,
    ST_X(pt.coordenada) AS longitude,
    ST_X(ST_Transform(pt.coordenada, 31983)) AS este_utm_23s,
    ST_Y(ST_Transform(pt.coordenada, 31983)) AS norte_utm_23s,
    ST_SRID(pt.coordenada) AS srid,
    pt.qualidade_fix
FROM pontos pt
WHERE pt.nome = 'P01';
-- Referencia atual validada no backend Python em:
-- C:\Users\User\Documents\Playground\services\api\app\services\geodesy.py
-- este_utm_23s ~= 186085.106223
-- norte_utm_23s ~= 8253307.867629
-- srid = 4674

SELECT
    tablename,
    tableowner,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

SELECT
    'PostGIS OK' AS status,
    postgis_version() AS versao
UNION ALL
SELECT
    'SIRGAS 2000 OK',
    proj4text
FROM spatial_ref_sys
WHERE srid = 4674;

SELECT
    (SELECT COUNT(*) FROM clientes WHERE deleted_at IS NULL) AS clientes,
    (SELECT COUNT(*) FROM projetos WHERE deleted_at IS NULL) AS projetos,
    (SELECT COUNT(*) FROM pontos WHERE deleted_at IS NULL) AS pontos,
    (SELECT COUNT(*) FROM camadas) AS camadas;
