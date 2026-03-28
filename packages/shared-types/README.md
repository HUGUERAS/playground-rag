# Shared Types

Contratos compartilhados do dominio `GeoAdmin`.

## Tipos candidatos

- Project
- Job
- Point
- Line
- Surface
- Layer
- Code
- UserProfile

## Estrutura atual

- `src/geoadmin_shared_types/domain.py`: modelos de dominio iniciais.
- `src/geoadmin_shared_types/calculations.py`: contratos para endpoints de calculo.
- `src/geoadmin_shared_types/health.py`: resposta padrao de healthcheck.

## Objetivo

Centralizar contratos usados pela API e, depois, pelos frontends e automacoes.

## Contratos geodesicos atuais

- `InverseRequest` e `InverseResponse`
- `AreaRequest` e `AreaResponse`
- `ConvertCoordinateRequest` e `ConvertCoordinateResponse`
- `ErrorResponse`
- `SubdivisionByAreaRequest`
- `SubdivisionByPercentualRequest`
- `SubdivisionByVertexRequest`
- `SubdivisionByFixedPointRequest`
- `SubdivisionResult`
