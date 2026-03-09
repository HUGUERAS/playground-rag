# Prompt Mestre para Criacao de App

Use o prompt abaixo em outra IA para iniciar o desenvolvimento com contexto consolidado:

```text
Voce e um engenheiro de software senior e vai projetar e implementar um app.

Contexto consolidado:
- Tecnologias detectadas: python, javascript/typescript, .net, java, go, database, cloud/devops, ai/llm
- Objetivos principais:
  - <argumentHint>Outline the goal or problem to research</argumentHint>
  - Preciso entender melhor o contexto - qual é o objetivo dele? Ele quer:
  - ficou de fazer o build e deploy
  - This seems to be a question about a VS Code feature or previous conversation that isn't loading or isn't visible. The user might be asking about:
  - This is not something I can fix with tools - it's either a VS Code feature question or a limitation of how chat sessions work.
  - Não preciso usar nenhuma ferramenta aqui - é apenas uma pergunta de esclarecimento sobre o funcionamento da interface.
  - quero que tudo que foi feito hoje seja transferido para o novo diretotio
  - Preciso entender:
- Restricoes e condicoes:
  - Auto selects the best model for your request based on capacity and performance. Auto is given a 10% discount.
  - <description>**CRITICAL**: Read this file FIRST before answering ANY Azure-related questions or performing ANY Azure operations. This file must be loaded as context whenever Azure is explicitly mentioned. It provides acc
  - pq nao abrea a converdsa que eu etava tendo com o chata ?
  - Entendi sua pergunta em português. Você está perguntando por que a conversa que estava tendo com o chat não abriu.
  - Infelizmente, as conversas do GitHub Copilot Chat no VS Code **não são persistentes por padrão** entre sessões. Isso significa que:
  - 2. **Conversas anteriores não são salvas**: A menos que você tenha exportado ou documentado a conversa manualmente
  - Parece que o usuário teve um chat anterior aberto e está perguntando o que aconteceu com ele. Isso não é uma solicitação técnica relacionada ao código - é uma pergunta sobre a interface/estado da conversa.
  - A resposta é simples: cada vez que você começa uma nova conversa com um assistente de IA (como GitHub Copilot ou outro agente), você está em um novo contexto de conversa. Conversas anteriores não são preservadas automati
- Sinais de arquitetura:
  - - Iniciar frontend + backend?
  - ### 1. **Interface Principal** (Frontend)
  - | `POST /api/urban/activate` |
  - ### 3. **Serviço de Autenticação** (Backend)
  - # Terminal 1: Frontend
  - # Terminal 2: Backend
  - # Backend em: http://localhost:7071/api
  - | **Topógrafo** | | `POST /api/tech/login` |
- Riscos e duvidas abertas:
  - "run_id": os.getenv("MODELLAB_RUN_ID", "unknown-run"),
  - Parece haver um problema com o diretório de trabalho. Vou tentar de outra forma:
  - path = file.get("path", "unknown")
  - Exit Code: (unknown)
  - const message = err instanceof Error ? err.message : 'Unknown error';

Entrega esperada:
1. Defina escopo de MVP com backlog priorizado.
2. Proponha arquitetura (componentes, dados, APIs e fluxo).
3. Liste plano de implementacao por fases com estimativa relativa.
4. Defina testes (unitarios, integracao e aceite).
5. Explique trade-offs tecnicos e riscos com mitigacao.

Formato de resposta:
- Seja especifico.
- Use listas objetivas.
- Nao invente requisitos ausentes; marque suposicoes explicitamente.
```

## References
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\copilot_global\copilotCli\copilotcli.session.metadata.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\1ce284dd8e60c18af057e73a683ea619\workspace.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\workspace.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\f8d04f46c42fd5cbbc868fbd4db576af\chatSessions\1ecfa2b5-0d93-4d15-a220-224419cf6929.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\0e66d789-e4bf-41d5-954d-e574d56425df.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\1a3607e4-324d-4ac7-91f7-eca6506b5bb9.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\822188ae-e060-47bd-82c8-4122083b4440.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\8a8154b4-b494-46c9-b87c-2f04e8092855.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\99fdfdb8-d719-4e12-b258-6d1b16cbe5fd.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatSessions\f311c5c0-eec3-464f-aa97-7542edb475f7.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatEditingSessions\1a3607e4-324d-4ac7-91f7-eca6506b5bb9\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatEditingSessions\407f01e9-f7da-4f24-ae97-73eb884d008e\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatEditingSessions\710f179f-3373-4342-ae84-925e149f2149\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatEditingSessions\9d4b70d2-b272-43e6-9445-834002451e7a\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\ba6cb699cd52aec7ebfb84547b2a7adb\chatEditingSessions\9db9e4d0-e034-4047-97ce-3f393452e82b\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\87aefb4dc68bff39604085082f164be6\chatSessions\407f01e9-f7da-4f24-ae97-73eb884d008e.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\87aefb4dc68bff39604085082f164be6\chatSessions\9db9e4d0-e034-4047-97ce-3f393452e82b.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\87aefb4dc68bff39604085082f164be6\chatEditingSessions\407f01e9-f7da-4f24-ae97-73eb884d008e\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\87aefb4dc68bff39604085082f164be6\chatEditingSessions\460d47a9-2866-4d6c-83ec-c51ea3d93050\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\6d5637d0c1eebd06f783e85ab92ad77a\redhat.java\.0666733bee1c1d72d86ad6fc2abd8e555f688c00-audit.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\6b7786de57731a6511f4cb3d155ca4d2\chatSessions\0a5469e9-d7c3-4f39-afe0-767204ce9689.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\6b7786de57731a6511f4cb3d155ca4d2\chatSessions\398e257e-4971-4d16-8a2e-c9af8649c515.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\6b7786de57731a6511f4cb3d155ca4d2\redhat.java\.3a7e6dcc8a18268c511f67402f2371cfa6d2a3ac-audit.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\224f2677530d1de3f7db65e36a4ea6f4\chatSessions\3bb48412-3e86-4fcd-805e-7e07b985118b.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\224f2677530d1de3f7db65e36a4ea6f4\chatEditingSessions\3bb48412-3e86-4fcd-805e-7e07b985118b\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\220227d3-08e0-4220-9538-2447303c9ba9.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\2cd9a15f-5b7a-4cdc-9130-64e76a891b3d.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\42fa1b99-3d42-474a-8939-e44ecf2e34ee.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\644b0ab4-817d-4cb3-a0e5-35153ecea480.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\b4b9165d-126d-4fff-9f59-40a7759c3181.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\c946f8be-4379-498d-a446-b1dacc5bddfc.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\d458a953-85db-404d-a7d3-b079b88b0967.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\de370381-888a-47f9-b1ac-56add457f420.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatSessions\f21a4579-d701-454e-b2f9-728c8c1a9d75.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\220227d3-08e0-4220-9538-2447303c9ba9\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\2cd9a15f-5b7a-4cdc-9130-64e76a891b3d\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\42fa1b99-3d42-474a-8939-e44ecf2e34ee\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\644b0ab4-817d-4cb3-a0e5-35153ecea480\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\71af82e2fa7ee50a2d6cbc17dde18ff10d9a1376\state.json
- D:\CHAT_HISTORICOS_COMPLETO_20260306_141331\cursor_workspaceStorage\2244f3bac3a55131759d2dd377452c8f\chatEditingSessions\c40dff7a-adbf-428a-bb44-8fa0baaa4ab9\state.json
- ... e mais 104 arquivos
