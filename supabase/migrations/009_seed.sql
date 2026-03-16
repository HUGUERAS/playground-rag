-- GeoAdmin Pro - Migration 009
-- Seed inicial

INSERT INTO clientes (nome, cpf_cnpj, telefone, municipio, estado)
VALUES ('CLIENTE TESTE GEOADMIN', '000.000.000-00', '(61) 99999-0000', 'Brasilia', 'DF')
ON CONFLICT (cpf_cnpj) DO NOTHING;

INSERT INTO projetos (
    cliente_id,
    nome,
    numero_job,
    municipio,
    estado,
    zona_utm,
    status
)
VALUES (
    (SELECT id FROM clientes WHERE cpf_cnpj = '000.000.000-00'),
    'Levantamento Teste - Chacara 01',
    '20260316000001',
    'Brasilia',
    'DF',
    '23S',
    'medicao'
)
ON CONFLICT (numero_job) DO NOTHING;

INSERT INTO pontos (
    projeto_id,
    nome,
    descricao,
    coordenada,
    altitude_m,
    qualidade_fix,
    hdop,
    num_satelites,
    camada
)
VALUES (
    (SELECT id FROM projetos WHERE numero_job = '20260316000001'),
    'P01',
    'Ponto de teste - Marco Zero Brasilia',
    ST_SetSRID(ST_MakePoint(-47.929722, -15.779167), 4674),
    1172.0,
    4,
    0.6,
    24,
    'PONTOS'
)
ON CONFLICT DO NOTHING;
