# Implementation Order GeoAdmin

## Fase 0 - Base operacional

- consolidar documentacao oficial
- fixar backlog e prioridades
- manter scripts de ingestao e revisao

## Fase 1 - Dados e backend

- modelar entidades no Supabase
- subir `FastAPI` no Railway
- implementar `health`, `inverso` e `area`
- definir storage de documentos e anexos

## Fase 2 - Web primeiro

- criar portal do cliente no Vercel
- criar backoffice web minimo
- integrar auth e storage do Supabase

## Fase 3 - Campo mobile

- iniciar app `Expo`
- levar para o mobile as areas `Projeto`, `Levantamento`, `Config` e `Ferramentas`
- priorizar coleta, camadas e sincronizacao

## Fase 4 - Escala e automacao

- mover jobs pesados para infraestrutura mais robusta se necessario
- avaliar Google Cloud para scheduler, fila ou workers dedicados

## Regra de prioridade

- o que define dado e regra vem antes do que desenha interface;
- o que e pesado fica fora do frontend;
- o que ainda e hipotese nao vira infraestrutura complexa.
