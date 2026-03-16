# Decision Log GeoAdmin

## Decisoes atuais

### 2026-03-16 - Precedencia editorial

- O `.zip` fornecido pelo usuario e a fonte oficial da base inicial.
- O `Google_Gemini_source.html` fica somente como trilha historica.
- As capturas do app validam nomenclatura e agrupamento funcional.

### 2026-03-16 - Organizacao por blocos

- A documentacao foi organizada em produto, planejamento, mapeamento funcional, referencia, arquivo de origem e governanca.
- O objetivo e permitir leitura rapida por pessoas e por agentes.

### 2026-03-16 - Foco inicial

- A camada documental e a primeira camada ativa do projeto.
- RAG e implementacao do app ficam para as proximas etapas.

### 2026-03-16 - Master Plan v2 adotado

- O `Master_Plan_v2_GeoAdmin.md` passa a ser a referencia principal de planejamento.
- O `Roadmap_GeoAdmin.md` continua util como resumo legado, mas nao dita mais a ordem de execucao.
- A implementacao deve seguir gates de fase e criterios de aceitacao explicitos.

### 2026-03-16 - Hardware GNSS definido

- A Task 0.2 foi concluida com o receptor `CHC Navigation i73+`.
- O protocolo de comunicacao com o app sera Bluetooth classico via SPP.
- O parser deve priorizar sentencas `GNGGA`, `GNGSA`, `GNRMC` e `PCHC`.
- A implementacao mobile deve usar `react-native-bluetooth-classic`, nao `react-native-ble-plx`.

### 2026-03-16 - Migrations Supabase estruturadas

- As migrations SQL oficiais foram organizadas em `infra/supabase/migrations`.
- A base armazena geometrias em `SRID 4674` e converte para UTM dinamicamente com base em `projetos.zona_utm`.
- Foi evitado hardcode de `EPSG:31983` em triggers e views para nao limitar o sistema a `23S`.
- A Task 0.3 so deve ser marcada como concluida apos execucao real no Supabase e verificacao do ponto seed.

### 2026-03-16 - Fase 0 encerrada e backend oficial unificado

- A Fase 0 passa a ser considerada concluida no projeto real.
- O projeto Supabase `jrlrlsotwsiidglcbifo` recebeu as migrations oficiais e teve o seed validado com sucesso.
- O backend oficial unico passa a ser `services/api`; a pasta `backend/` foi descartada para eliminar duplicidade de manutencao.
- As rotas de `projetos` foram conectadas ao Supabase e a base inicial recebeu import de pastas reais de trabalho, chegando a `38` clientes e `38` projetos.
- A Fase 1 segue aberta apenas para as entregas de produto que ainda nao foram concluídas, especialmente persistencia detalhada de pontos, importacao tecnica e camada mobile.
