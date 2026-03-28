-- GeoAdmin Pro - Migration 008
-- Views uteis

CREATE OR REPLACE VIEW vw_projetos_completo AS
SELECT
    p.id,
    p.numero_job,
    p.nome AS projeto_nome,
    p.status,
    p.zona_utm,
    p.data_medicao,
    p.data_protocolo,
    p.prazo_estimado,
    p.valor_servico,
    p.valor_pago,
    p.valor_servico - p.valor_pago AS saldo_devedor,
    c.nome AS cliente_nome,
    c.cpf_cnpj,
    c.telefone,
    c.email,
    c.municipio AS cliente_municipio,
    (
        SELECT COUNT(*)
        FROM pontos pt
        WHERE pt.projeto_id = p.id
          AND pt.deleted_at IS NULL
    ) AS total_pontos,
    p.criado_em,
    p.atualizado_em
FROM projetos p
LEFT JOIN clientes c ON c.id = p.cliente_id
WHERE p.deleted_at IS NULL;

COMMENT ON VIEW vw_projetos_completo IS 'Visao desnormalizada para o dashboard principal do app.';

CREATE OR REPLACE VIEW vw_pontos_utm AS
SELECT
    pt.id,
    pt.projeto_id,
    pt.nome,
    pt.descricao,
    pt.codigo,
    pt.camada,
    pt.qualidade_fix,
    pt.hdop,
    pt.altitude_m,
    pt.num_amostras,
    pt.coletado_em,
    pt.sincronizado,
    ST_Y(pt.coordenada) AS latitude,
    ST_X(pt.coordenada) AS longitude,
    pr.zona_utm,
    utm_srid_por_zona(pr.zona_utm) AS srid_utm,
    ST_X(ST_Transform(pt.coordenada, utm_srid_por_zona(pr.zona_utm))) AS este_utm,
    ST_Y(ST_Transform(pt.coordenada, utm_srid_por_zona(pr.zona_utm))) AS norte_utm
FROM pontos pt
JOIN projetos pr ON pr.id = pt.projeto_id
WHERE pt.deleted_at IS NULL;

COMMENT ON VIEW vw_pontos_utm IS 'Pontos com coordenadas UTM dinamicas conforme zona_utm do projeto.';

CREATE OR REPLACE VIEW vw_alertas_prazo AS
SELECT
    p.id,
    p.numero_job,
    p.nome,
    p.status,
    c.nome AS cliente_nome,
    c.telefone,
    p.prazo_estimado,
    NOW()::date - p.prazo_estimado AS dias_atraso,
    CASE
        WHEN p.prazo_estimado < NOW()::date THEN 'VENCIDO'
        WHEN p.prazo_estimado <= NOW()::date + 7 THEN 'VENCE_EM_7_DIAS'
        WHEN p.prazo_estimado <= NOW()::date + 30 THEN 'VENCE_EM_30_DIAS'
        ELSE 'OK'
    END AS situacao_prazo
FROM projetos p
LEFT JOIN clientes c ON c.id = p.cliente_id
WHERE p.deleted_at IS NULL
  AND p.status <> 'finalizado'
  AND p.prazo_estimado IS NOT NULL;

COMMENT ON VIEW vw_alertas_prazo IS 'Projetos em atraso ou proximos do prazo. Para notificacoes automaticas.';
