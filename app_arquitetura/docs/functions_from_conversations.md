# Funcoes Derivadas Das Conversas

Fonte consolidada utilizada:
- `chat_context_output_real_20260309_run_now/consolidated_conversations.md`
- Total de fontes lidas na consolidacao: 161

## 1. Fluxo por perfil (onboarding)

Sinais recorrentes nas conversas:
- `Topografo`
- `Proprietario`
- `Agricultor`
- `POST /api/tech/login`
- `POST /api/rural/onboard`
- `POST /api/urban/activate`

Funcoes implementadas no app:
- `POST /api/tech/login`: autenticacao MVP do perfil Topografo.
- `POST /api/rural/onboard`: registro de onboarding rural (Proprietario).
- `POST /api/urban/activate`: ativacao urbana (Agricultor).
- `GET /api/onboarding/snapshot`: estado agregado dos fluxos acima.

## 2. Orquestracao operacional

Sinais recorrentes nas conversas:
- start/stop/status de automacao
- comandos de terminal para backend/frontend

Funcoes implementadas no app:
- `POST /metrica/start`
- `POST /metrica/stop`
- `GET /metrica/status`

## 3. RAG tecnico

Sinais recorrentes nas conversas:
- perguntas ao RAG
- reindexacao de base

Funcoes implementadas no app:
- `POST /rag/reindex`
- `POST /rag/query`

## 4. Interface unica web

Sinais recorrentes nas conversas:
- "Iniciar frontend + backend"
- necessidade de painel unico e fluxo completo

Funcoes implementadas no frontend:
- Painel Health/Funcoes.
- Login Topografo.
- Formulario Rural Onboard.
- Formulario Urban Activate.
- Painel RAG.
- Painel Metrica.

## 5. Endpoints de apoio

- `GET /`: entrega o frontend integrado.
- `GET /health`: estado da API + disponibilidade do RAG.
- `GET /api/spec/functions`: catalogo das funcoes ativadas no MVP.
