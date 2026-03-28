# Documentation Backlog GeoAdmin

## Prioridade alta

- Detalhar o fluxo de coleta e sincronizacao offline do modulo de campo.
- Implementar `nmea_parser.py` para o CHC i73+ com foco em `GNGGA` e `PCHC`.
- Transformar a lista de ferramentas geometricas em backlog tecnico com entradas, saidas e validacoes.
- Formalizar `Camadas` como entidade funcional com comportamento e origem.
- Especificar `Vista CAD` como componente com operacoes de selecao, edicao e medicao.

## Prioridade media

- Documentar importacao e exportacao de formatos tecnicos.
- Relacionar `Projetos`, `jobs` e estrutura de dados do levantamento.
- Descrever impacto de `Unidades`, `Decimais`, `Coordenadas`, `GNSS` e `TS` nos calculos e persistencia.
- Registrar politica de armazenamento para imagens e arquivos de mapa.

## Prioridade baixa

- Refinar o modulo do cliente com jornadas e documentos esperados.
- Expandir regras de auditoria e rollback por fluxo.
- Catalogar mensagens amigaveis de erro por grupo funcional.

## Itens que nao devem ser feitos agora

- Reescrever o app inteiro a partir das telas sem antes fechar backlog e regra de negocio.
- Indexar HTML bruto no fluxo principal de trabalho.
- Tratar o pacote de origem como documento final.
