# Supabase GeoAdmin

Migrations SQL oficiais do `GeoAdmin Pro` para Supabase/PostGIS.

## Ordem de execucao

Execute os arquivos da pasta `migrations/` em ordem numerica no SQL Editor do Supabase.

## Convencoes

- IDs: `UUID` gerados com `gen_random_uuid()`
- Datas: `TIMESTAMPTZ`
- Geometrias base: `SRID 4674` (`SIRGAS 2000`)
- Soft delete: `deleted_at`
- Calculos metricos: feitos em UTM dinamica a partir de `projetos.zona_utm`

## Observacoes importantes

- As geometrias sao armazenadas em coordenadas geograficas (`4674`) para manter consistencia com PostGIS e com a coleta GNSS.
- As views e triggers convertem para UTM usando uma funcao auxiliar que respeita a `zona_utm` do projeto.
- O ponto seed de Brasilia usa `lat=-15.779167`, `lon=-47.929722` e `altitude_m=1172.0`.
- No backend atual, esse ponto converte para `E=186085.106223` e `N=8253307.867629` em `EPSG:31983`.
