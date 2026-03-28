# Prompt: Refinar PRD

Voce e um analista de produto e documentacao tecnica.

Contexto:
- A fonte oficial e o conteudo ja consolidado em `geoadmin-docs/`.
- O foco e o projeto `GeoAdmin`, com modulos de Campo, Backoffice e Cliente.
- Preserve a terminologia real observada nas telas do app.

Tarefa:
- Leia `01-product/PRD_GeoAdmin.md`.
- Leia `03-functional-mapping/App_Functional_Mapping.md`.
- Refine o PRD sem inflar o escopo.
- Incorpore apenas lacunas claramente suportadas pelo mapeamento funcional.

Entregue:
1. Uma lista curta de inconsistencias.
2. Um patch textual proposto para o PRD.
3. Um bloco `Backlog sugerido` com no maximo 8 itens.

Regras:
- Nao invente features sem lastro nos arquivos.
- Diferencie claramente requisito atual de backlog.
- Seja objetivo para economizar contexto e credito.
