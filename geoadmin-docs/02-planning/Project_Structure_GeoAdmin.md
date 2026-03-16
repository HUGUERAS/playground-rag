# Project Structure GeoAdmin

## Estrutura sugerida do repositorio

```text
apps/
  backoffice-web/
  client-portal/
  mobile-field/
services/
  api/
packages/
  shared-types/
  shared-utils/
infra/
  github/
docs/
  geoadmin-docs/
scripts/
prompts/
```

## Papel de cada pasta

### `apps/backoffice-web`

- painel administrativo web
- listas, filtros, dashboard e acompanhamento interno
- deploy no Vercel

### `apps/client-portal`

- portal do cliente
- login por magic link
- upload de documentos
- consulta de status
- deploy no Vercel

### `apps/mobile-field`

- app mobile do topografo
- coleta, camadas, vista CAD e ferramentas de campo
- React Native com Expo

### `services/api`

- backend `FastAPI`
- validacoes
- calculos
- exportacoes
- automacoes
- deploy inicial no Railway

### `packages/shared-types`

- contratos compartilhados
- tipos de dominio como projeto, ponto, camada, job e usuario

### `packages/shared-utils`

- validacoes reutilizaveis
- helpers de formato
- normalizacao de dados compartilhada entre apps e servicos

### `infra/github`

- workflows do GitHub Actions
- padroes de CI
- templates de issue e PR quando fizer sentido

### `docs/geoadmin-docs`

- base documental consolidada
- PRD, roadmap, mapeamento funcional e governanca

## Ordem sugerida de criacao

1. `services/api`
2. `packages/shared-types`
3. `apps/client-portal`
4. `apps/backoffice-web`
5. `apps/mobile-field`

## Estrategia de crescimento

- Comece pelo backend e pelos tipos compartilhados.
- Suba o portal web antes do app mobile completo, se quiser validar fluxo de cliente mais cedo.
- Deixe a camada `infra/` minima enquanto a arquitetura ainda estiver estabilizando.
