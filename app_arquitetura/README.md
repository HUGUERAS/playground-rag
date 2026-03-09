# App Arquitetura Integrada

Este projeto define a arquitetura alvo para um app unico que aproveita:

- RAG local (FAISS + Ollama)
- Automacao Metrica (pipeline real + dashboard)
- API consolidada para frontend web/mobile

## Objetivo

Unificar os fluxos em um backend unico para:

1. Reindexar e consultar base RAG
2. Iniciar/monitorar jobs da automacao Metrica
3. Expor estado e logs para uma UI unica

## Estrutura

- `docs/architecture.md`: desenho da arquitetura e fluxo
- `docs/functions_from_conversations.md`: funcoes inferidas das conversas consolidadas
- `backend/main.py`: API FastAPI com endpoints-base

## Como executar (backend)

1. Instalar dependencias:

```powershell
pip install fastapi uvicorn
```

1. Rodar API:

```powershell
uvicorn app_arquitetura.backend.main:app --reload --port 8080
```

1. Abrir app no navegador:

```text
http://127.0.0.1:8080
```

## Frontend

- Arquivo: `app_arquitetura/frontend/index.html`
- O frontend e servido pela propria API no endpoint `/`.
- Painel com:
  - Health da API
  - Consulta/Reindex RAG
  - Start/Stop/Status da automacao Metrica

## Endpoints iniciais

- `GET /health`
- `GET /api/spec/functions`
- `POST /api/tech/login`
- `POST /api/rural/onboard`
- `POST /api/urban/activate`
- `GET /api/onboarding/snapshot`
- `POST /rag/reindex`
- `POST /rag/query`
- `POST /metrica/start`
- `POST /metrica/stop`
- `GET /metrica/status`

## Proximo passo recomendado

Conectar um frontend unico (React/Vue) nesses endpoints para substituir o controle manual por multiplas telas e scripts separados.
