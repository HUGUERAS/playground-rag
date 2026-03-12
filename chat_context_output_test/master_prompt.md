# Prompt Mestre para Criacao de App

Use o prompt abaixo em outra IA para iniciar o desenvolvimento com contexto consolidado:

```text
Voce e um engenheiro de software senior e vai projetar e implementar um app.

Contexto consolidado:
- Tecnologias detectadas: javascript/typescript, go, database, cloud/devops, ai/llm
- Objetivos principais:
  - Remember: Your goal is searching efficiently through MAXIMUM PARALLELISM to report concise and clear answers.
  - argument-hint: Outline the goal or problem to research
  - If research reveals major ambiguities or if you need to validate assumptions:
  - - If answers significantly change the scope, loop back to **Discovery**
  - - Explicit scope boundaries — what's included and what's deliberately excluded
  - - {Decision, assumptions, and includes/excluded scope}
- Restricoes e condicoes:
  - Save the comprehensive plan document to `/memories/session/plan.md` via #tool:vscode/memory, then show the scannable plan to the user for review. You MUST show plan to the user, as the plan file is for persistence only, 
  - - The plan MUST be presented to the user, don't just mention the plan file.
- Sinais de arquitetura:
  - Read more about proposed API at: https://code.visualstudio.com/api/advanced-topics/using-proposed-api
  - "enable-proposed-api": [""]
  - - **API and library questions**: How do I use this API? What does this method expect?
  - c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\AGENT_INSTRUCTIONS.md
  - c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\BACKEND_REVIEW.md
  - c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-3-frontend-engineer\AGENT_INSTRUCTIONS.md
  - c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\deploy-backend.ps1
  - Run the *Explore* subagent to gather context, analogous existing features to use as implementation templates, and potential blockers or ambiguities. When the task spans multiple independent areas (e.g., frontend + backen
- Riscos e duvidas abertas:
  - Riscos nao explicitados claramente nas conversas extraidas.

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
- C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\api.json
- C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\ask-agent\Ask.agent.md
- C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\copilotCli\copilotcli.session.metadata.json
- C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\explore-agent\Explore.agent.md
- C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\plan-agent\Plan.agent.md
- C:\Users\User\AppData\Roaming\Code\User\workspaceStorage\0010d70cd6e65ecb79a3ac5e6b167e45\workspace.json
