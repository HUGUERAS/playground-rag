# Documentation Workflow GeoAdmin

## Objetivo

Definir como a documentacao do `GeoAdmin` deve evoluir sem perder rastreabilidade nem inflar o escopo.

## Fluxo editorial

1. Fonte nova entra em `05-source-archive`.
2. Conteudo oficial e promovido para um documento existente ou para um novo documento curado.
3. Mudancas funcionais devem atualizar ao menos um destes blocos:
   - `01-product`
   - `02-planning`
   - `03-functional-mapping`
   - `04-reference`
4. Toda lacuna descoberta deve virar backlog ou regra explicita.

## Regra de promocao

- `05-source-archive` nunca e a fonte de trabalho diario.
- `01-product` descreve o que o sistema e e por que existe.
- `02-planning` descreve o que vem primeiro, depois e fora do MVP.
- `03-functional-mapping` conecta interface real, dados e backlog.
- `04-reference` guarda instrucoes operacionais, formulas e validacoes.

## Quando abrir um documento novo

Abra um documento novo apenas se uma destas condicoes for verdadeira:

- o assunto nao cabe claramente em um documento existente;
- o conteudo vai ser consultado de forma recorrente;
- misturar o novo assunto no documento atual tornaria a leitura ambigua.

## Quando editar um documento existente

Edite o documento existente quando a mudanca:

- esclarece requisito, termo ou regra;
- adiciona detalhe funcional de uma area ja mapeada;
- corrige conflito entre tela, PRD e roadmap.

## Regra de nomenclatura

- nomes de arquivos devem ser curtos, descritivos e em ASCII quando possivel;
- titulos internos podem preservar o nome real da feature do app;
- nomes mostrados nas telas prevalecem sobre apelidos internos, com alias documentado quando necessario.
