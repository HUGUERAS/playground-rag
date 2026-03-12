# Arquitetura do App Unificado

## 1. Visao Geral

O app unificado orquestra dois dominios principais:

- Dominio A: RAG tecnico local
- Dominio B: Automacao operacional Metrica

A API central elimina acoplamento direto do frontend com scripts e CLIs.

## 2. Componentes

1. API Gateway (FastAPI)

- Recebe requests do frontend
- Encaminha para servicos internos

1. RAG Service

- Reindexacao de documentos
- Consulta semantica com contexto
- Cache de chain para reduzir latencia

1. Metrica Service

- Start/stop de jobs de automacao
- Leitura de status, progresso e logs
- Controle de lote (fila)

1. Storage Local

- Base de docs: pasta coletada (`D:\PROGRAMACAO_COLETA_*`)
- Vetor: `faiss_db`
- Logs/artefatos: `automacao/metrica/logs` e `batch_runs`

1. Frontend Unico

- Painel RAG
- Painel Jobs Metrica
- Painel de logs e auditoria

## 3. Fluxos

### 3.1 Reindexacao RAG

Frontend -> `POST /rag/reindex` -> RAG Service -> gera FAISS -> retorna status.

### 3.2 Consulta RAG

Frontend -> `POST /rag/query` -> RAG Service -> resposta curta + contexto fonte.

### 3.3 Execucao Metrica

Frontend -> `POST /metrica/start` -> Metrica Service -> script PowerShell -> status e logs.

## 4. Contratos API (MVP)

- `GET /health`
- `POST /rag/reindex`
- `POST /rag/query`
- `POST /metrica/start`
- `POST /metrica/stop`
- `GET /metrica/status`

## 5. Nao-funcionais

- Idempotencia em start/stop
- Timeouts para scripts longos
- Logs estruturados por request/job
- Controle de concorrencia (1 job critico por vez)
- Fallback quando Ollama indisponivel

## 6. Roadmap

1. MVP API unica (este passo)
2. Integracao frontend unico
3. Observabilidade (metricas + tracing)
4. Controle de permissao por role
5. Empacotamento para execucao desktop (opcional)
