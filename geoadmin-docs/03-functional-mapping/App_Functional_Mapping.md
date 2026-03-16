# App Functional Mapping GeoAdmin

## Objetivo

Este documento relaciona as telas observadas do app com os modulos descritos no PRD e com o backlog funcional. As capturas foram tratadas como validacao da nomenclatura real usada pelo operador em campo.

## Area: Projeto

### Objetivo da area

Centralizar as entidades-base do trabalho tecnico.

### Acoes visiveis

- Abrir `Projetos`.
- Gerenciar `Sistema de coordenadas`.
- Acessar `Pontos`, `Linhas`, `Superficies`, `Imagens`, `Codigos` e `Camadas`.
- Executar `Importar`, `Exportar` e `Mais`.

### Dados manipulados

- Projetos e jobs.
- Pontos coletados.
- Linhas e superficies derivadas.
- Imagens de apoio.
- Codigos e camadas de trabalho.
- Arquivos importados e exportados.

### Vinculo com o PRD

- Principalmente `Modulo de Campo`.
- Apoia `Modulo Backoffice` ao estruturar entidades e organizacao de projetos.

### Gaps identificados

- O PRD cita projetos e lotes, mas ainda nao detalha linhas, superficies, codigos e imagens como entidades formais.
- Importacao e exportacao aparecem na interface real, mas ainda carecem de fluxo documentado.

## Area: Levantamento

### Objetivo da area

Abrigar as operacoes do levantamento e a coleta em campo.

### Acoes inferidas a partir do app e do contexto

- Coletar e salvar pontos.
- Trabalhar com visualizacao tecnica e desenho.
- Acessar informacoes de dados e medicao.

### Dados manipulados

- Coordenadas de pontos.
- Observacoes de levantamento.
- Geometrias intermediarias e resultado de medicao.

### Vinculo com o PRD

- `Modulo de Campo`, com foco em precisao GNSS e produtividade de campo.

### Gaps identificados

- Falta detalhar no PRD o fluxo completo de coleta, edicao, sincronizacao e recuperacao offline.

## Area: Config

### Objetivo da area

Controlar o comportamento do app e os parametros tecnicos do projeto.

### Acoes visiveis

- Ajustar `Definicoes de software`.
- Configurar `Auto Ok`.
- Controlar uso de uppercase para codigos, descricoes e nomes de pontos.
- Ajustar `Unidades`, `Decimais`, `Coordenadas`, `GNSS`, `TS` e `Definicoes de visualizacao`.

### Dados manipulados

- Preferencias de interface.
- Parametros de projeto.
- Regras de entrada de dados.
- Configuracoes de equipamentos e representacao.

### Vinculo com o PRD

- `Modulo de Campo` para operacao.
- `Modulo Backoffice` no que toca padronizacao de dados.

### Gaps identificados

- O material original nao documenta ainda como essas configuracoes afetam calculos, persistencia e sincronizacao.

## Area: Ferramentas

### Objetivo da area

Oferecer utilitarios tecnicos e calculos geometricos de uso rapido.

### Ferramentas observadas

- Ajuste do mapa.
- Volume.
- Area.
- Inverso.
- Plotar escritura.
- Transformacao.
- Subdivisao de area.
- Conversao angular.
- Calculo dos parametros.
- Distancia ponto a linha.
- Distancia de desvio.
- Deflexao.
- Rotacao.
- Interseccao.
- Angulo de bisseccao.
- Linha divisoria.
- Tangent point.
- Media de pontos.
- Least squares.

### Dados manipulados

- Pontos, linhas, angulos, superficies e parametros de transformacao.

### Vinculo com o PRD

- Nucleo do `Modulo de Campo`.
- Parte da API de calculos do backend.

### Gaps identificados

- O PRD explicita somente `Inverso` e menciona `Area` de forma indireta.
- A lista completa de ferramentas precisa virar backlog tecnico, com definicao de formula, entrada, saida e validacoes para cada funcao.

## Area: Vista CAD

### Objetivo da area

Permitir leitura, selecao e edicao visual das geometrias do projeto.

### Acoes visiveis

- Selecionar visivel.
- Selecionar invisivel.
- Salvar ponto.
- Explodir.
- Mesclar.
- Controlar visualizacao de camadas.
- Navegar entre `Dados`, `Desenho` e `Medida`.

### Dados manipulados

- Geometrias do desenho.
- Visibilidade e estado de selecao.
- Ponto atual de trabalho.

### Vinculo com o PRD

- `Modulo de Campo`.

### Gaps identificados

- O PRD ainda nao descreve o canvas CAD como componente funcional.
- Falta detalhar quais operacoes editam a geometria e quais apenas auxiliam a visualizacao.

## Area: Camadas

### Objetivo da area

Gerenciar a separacao logica e visual dos elementos tecnicos do projeto.

### Acoes visiveis

- Listar camadas de trabalho.
- Navegar por `Camadas de trabalho`, `Arquivos de mapas` e `Mapa online`.
- Criar nova camada.
- Ativar ou revisar camadas com nomes como `auto top`, `Fronteira do levantamento`, `Pc 01` e `PONTOS`.

### Dados manipulados

- Metadados de camada.
- Estado de visibilidade e organizacao.
- Vinculo de elementos tecnicos a agrupamentos logicos.

### Vinculo com o PRD

- `Modulo de Campo`.
- Suporte para organizacao e futura auditabilidade no `Modulo Backoffice`.

### Gaps identificados

- O material original nao define modelo de dados, permissao ou comportamento de camadas.
- A relacao entre camadas locais, arquivos de mapa e mapa online precisa ser especificada.

## Backlog funcional sugerido a partir das telas

- Formalizar `Camadas` como entidade persistente com visibilidade e origem.
- Especificar `Vista CAD` com operacoes de selecao, edicao e medicao.
- Definir contratos de importacao e exportacao para formatos tecnicos.
- Catalogar cada ferramenta geometrica com formula, validacoes e erros esperados.
- Documentar configuracoes que impactam padrao de dados e compatibilidade com equipamentos.

## Itens ausentes ou ambiguos

- Fluxo detalhado de sincronizacao offline.
- Regra de permissao por perfil dentro do app mobile.
- Relacao entre `Projetos` e `job-20260315013402`.
- Politica de persistencia para imagens e arquivos de mapa.
