# Master Plan v2 - GeoAdmin Pro
**Versao:** 2.0 | **Status:** Em Desenvolvimento | **Autor:** Hugo (Desenrola Team)

> Este documento substitui o `Roadmap_GeoAdmin.md` como referencia principal de planejamento. Cada ponto fraco identificado foi convertido em tasks concretas com criterios de aceitacao. Nenhuma fase avanca sem os criterios da fase anterior estarem satisfeitos.

---

## Decisao de Stack

O projeto original foi planejado com Flutter e depois mudou para React Native sem documentar o motivo. Essa decisao precisa ser feita agora, pois impacta tudo.

| Criterio | React Native (Expo) | Flutter (Dart) |
|---|---|---|
| Renderizacao CAD (canvas pesado) | Limitado | Nativo e robusto |
| Bluetooth GNSS serial (NMEA) | Requer libs externas | Suporte nativo via FFI |
| Curva de aprendizado | JavaScript (familiar) | Dart (nova linguagem) |
| Comunidade GIS mobile | Pequena | Crescente |
| Deploy rapido MVP | Melhor (Expo Go) | Medio |

**Recomendacao:** Use React Native para o MVP (Fases 1 e 2). Se a renderizacao CAD travar ou a conexao GNSS nao funcionar de forma confiavel, migre o modulo especifico para Flutter, nao o app inteiro.

**Decisao tomada em:** `____/____/______` | **Por:** `__________________`

---

## Fase 0 - Validacao

> **Por que existe:** Erros de calculo geodesico em producao podem invalidar escrituras no INCRA. Esta fase cria a "muralha matematica" que protege todo o resto.

### Task 0.1 - Gabarito de Testes Matematicos
**Responsavel:** Hugo (revisao humana obrigatoria) | **Ferramenta:** Python puro

Criar um arquivo `backend/tests/gabarito_geodesico.py` com pares de entrada/saida calculados manualmente ou retirados de software certificado.

```text
Caso 1 - Inverso:
  Entrada: P1(313500.000000, 7395000.000000), P2(313800.000000, 7395400.000000)
  Esperado: Distancia = 500.000000m, Azimute = 36°52'11.63"

Caso 2 - Area (Gauss):
  Entrada: poligono de 4 vertices conhecidos
  Esperado: area = X.XXXXXX m2

Caso 3 - Conversao SIRGAS 2000 -> UTM Zona 23S:
  Entrada: Lat -15.779167, Lon -47.929722
  Esperado: E=191000.000m, N=8254000.000m (verificar)
```

**Criterio de aceitacao:** Cada funcao do backend deve passar em 100% dos casos do gabarito antes de ser integrada ao app. Tolerancia maxima: +-0.001m em distancias, +-0.001" em angulos.

### Task 0.2 - Decisao de Tecnologia GNSS
**Responsavel:** Hugo | **Ferramenta:** Pesquisa + teste de hardware

**Status atual:** Concluida  
**Receptor definido:** `CHC Navigation i73+`  
**Documento oficial:** `04-reference/hardware/receptor_gnss_chc_i73_plus.md`

Antes de escrever codigo de campo, responder:

1. Qual receptor GNSS sera usado?
2. O receptor se conecta via Bluetooth classico ou BLE?
3. As sentencas NMEA sao padrao ou possuem extensoes proprietarias?
4. O receptor suporta NTRIP via celular ou precisa de radio UHF?

**Criar:** `docs/hardware/receptor_gnss.md` com as respostas.

**Criterio de aceitacao:** Script Python standalone `backend/geo/nmea_parser.py` que le um arquivo `.txt` com sentencas NMEA do receptor especifico e extrai latitude, longitude, altitude, HDOP, numero de satelites e status de fix.

### Task 0.3 - Configurar Supabase com PostGIS
**Responsavel:** Arquiteto de Dados | **Ferramenta:** Supabase + SQL

**Status atual:** Concluida. Migrations executadas no projeto Supabase `jrlrlsotwsiidglcbifo`, seed validado e endpoints iniciais de `projetos` ligados ao backend oficial em `services/api`.

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE projetos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  cliente_id UUID,
  status TEXT CHECK (status IN ('medicao','montagem','protocolado','aprovado','finalizado')),
  zona_utm TEXT DEFAULT '23S',
  srid INTEGER DEFAULT 4674,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pontos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  projeto_id UUID REFERENCES projetos(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  coordenada GEOMETRY(POINT, 4674) NOT NULL,
  altitude NUMERIC(10,4),
  descricao TEXT,
  camada TEXT DEFAULT 'PONTOS',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE clientes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  cpf_cnpj TEXT UNIQUE,
  telefone TEXT,
  email TEXT,
  magic_link_token UUID,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Criterio de aceitacao:** Inserir e recuperar um ponto com coordenada real de Brasilia e confirmar que o SRID 4674 esta correto na consulta `ST_SRID()`.

**Validacao executada em 2026-03-16:**
- `supabase link --project-ref jrlrlsotwsiidglcbifo`
- `supabase db push`
- seed confirmado no banco remoto com `1` cliente, `1` projeto, `1` ponto e `6` camadas padrao
- base expandida com import inicial das pastas reais de trabalho, totalizando `38` clientes e `38` projetos
- leitura real validada via `GET /projetos` e `GET /projetos/{id}` no backend oficial

---

## Fase 1 - Nucleo Tecnico

> **Meta:** Um topografo consegue abrir o app, criar um projeto, digitar pontos manualmente e ver o calculo de Inverso e Area funcionando com precisao certificada.

### Task 1.1 - Backend: API de Calculos
**Agente:** Engenheiro Geografico | **Ferramenta:** FastAPI + Pyproj + Shapely

**Status atual:** Parcialmente concluida no backend oficial `services/api`. Os endpoints geodesicos estao ativos, o backend duplicado `backend/` foi descartado e os testes automatizados da API estao verdes.

| Endpoint | Entrada | Saida |
|---|---|---|
| `POST /geo/inverso` | `{x1,y1,x2,y2}` | `{distancia, azimute_decimal, azimute_graus_ms}` |
| `POST /geo/area` | `{pontos: [{x,y}]}` | `{area_m2, perimetro_m}` |
| `POST /geo/converter` | `{lat, lon, zona}` | `{este, norte, zona, srid}` |

**Regras inegociaveis:**
- 6 casas decimais em todas as saidas numericas.
- Proibido `try: except: pass`.
- Rodar `shape.is_valid` antes de qualquer calculo de area.
- Cada funcao deve ter o gabarito da Task 0.1 como teste automatizado com `pytest`.

**Criterio de aceitacao:** `pytest backend/tests/` com 100% de aprovacao no gabarito geodesico.

### Task 1.2 - Mobile: Estrutura de Abas e Navegacao
**Agente:** Arquiteto UI/UX | **Ferramenta:** React Native + Expo Router

```text
app/
  (tabs)/
    _layout.tsx
    projeto/
      index.tsx
      [id].tsx
    calculos/
      index.tsx
      inverso.tsx
      area.tsx
      conversao.tsx
    clientes/
      index.tsx
      [id].tsx
    mapa/
      index.tsx
```

**Criterio de aceitacao:** App abre no celular via Expo Go, navega entre as 4 abas sem crash, grade de ferramentas exibe icones com legenda legivel sob luz solar direta.

### Task 1.3 - Mobile: Tela de Calculo Inverso
**Agente:** UI/UX + Engenheiro Geografico | **Ferramenta:** React Native + fetch

Campos: Nome P1, Norte P1, Este P1, Nome P2, Norte P2, Este P2. Botao "Calcular" chama `POST /geo/inverso`. Botao "Salvar no Projeto" salva no Supabase.

**Criterio de aceitacao:** Calcular o Caso 1 do gabarito no app e obter o mesmo resultado. Testar sem internet com erro amigavel e codigo tecnico, sem crash.

### Task 1.4 - Modo Offline: Fila de Sincronizacao
**Agente:** Arquiteto de Dados | **Ferramenta:** WatermelonDB ou SQLite local

```text
Coletar ponto -> salvar SQLite local -> flag pendente_sync=true
Ao recuperar internet -> enviar para Supabase -> atualizar flag synced=true
Na tela -> icone de nuvem com contador de itens pendentes
```

**Criterio de aceitacao:** Coletar 10 pontos com o celular em modo aviao, ligar o Wi-Fi e confirmar que todos os 10 chegaram ao Supabase sem duplicatas.

---

## Fase 2 - Campo

> **Pre-requisito:** Task 0.2 concluida e receptor GNSS fisico em maos para testes.

### Task 2.1 - Modulo GNSS: Leitura Bluetooth
**Agente:** Engenheiro Geografico | **Ferramenta:** `react-native-bluetooth-classic`

```text
1. App escaneia dispositivos Bluetooth
2. Usuario seleciona o receptor pelo nome
3. App le sentencas NMEA em loop
4. Parser extrai posicao, HDOP, satelites e status
5. Coordenada aparece em tempo real na tela de coleta
```

**Premissa fechada para esta task:** O CHC i73+ usa Bluetooth classico SPP e nao BLE.

**Criterio de aceitacao:** Com o receptor fixo em um ponto de coordenadas conhecidas, o app deve exibir coordenadas com erro inferior ao limite do equipamento utilizado.

### Task 2.2 - Vista CAD Simplificada
**Agente:** Arquiteto UI/UX | **Ferramenta:** `react-native-svg` ou `react-native-canvas`

Funcionalidades minimas:
- plotar pontos coletados como circulos com nome;
- ligar pontos em sequencia formando linhas;
- zoom por pinca e pan por toque;
- exibir coordenada ao tocar em um ponto;
- exportar a vista como imagem PNG.

**Nao entra nesta fase:** edicao de geometria, importacao de DXF, renderizacao de superficies 3D.

**Criterio de aceitacao:** Plotar os vertices de uma area conhecida, verificar visualmente que o poligono fecha corretamente e que a proporcao do desenho corresponde ao terreno real.

### Task 2.3 - Importacao/Exportacao de Dados
**Agente:** Mestre da Automacao | **Ferramenta:** `ezdxf` + parser CSV

Formatos de entrada: CSV, TXT. Formatos de saida: CSV, DXF e KML.

**Criterio de aceitacao:** Exportar os pontos de um projeto real para DXF, abrir no Metrrica TOPO e confirmar que as coordenadas batem com as do app.

---

## Fase 3 - Administrativo e Cliente

> **Pre-requisito:** Fases 0, 1 e 2 concluidas e o app sendo usado em pelo menos 1 levantamento real.

### Task 3.1 - CRM de Processos
**Agente:** Arquiteto de Dados + UI/UX

Funcionalidades:
- cadastro de cliente com CPF/CNPJ, telefone, email e documentos;
- vinculacao cliente -> projeto -> processo;
- status com datas;
- campo de observacoes por etapa;
- alerta de prazo.

**Criterio de aceitacao:** Registrar um processo real do inicio ao fim, incluindo upload do PDF da matricula do imovel.

### Task 3.2 - Portal do Cliente (Magic Link)
**Agente:** Arquiteto de Dados + UI/UX | **Ferramenta:** Supabase Auth + React Native Web ou PWA

```text
Topografo clica em enviar link
Sistema gera token unico e envia via WhatsApp/SMS
Cliente abre o link no celular sem instalar app
Cliente ve status, documentos para assinar e arquivos finais para baixar
```

**Atencao:** Aprovacao da API do WhatsApp Business pode levar semanas. Iniciar esse processo no comeco da fase 3.

**Criterio de aceitacao:** Um cliente real consegue abrir o link, ver o status correto do processo e baixar o PDF sem pedir ajuda.

### Task 3.3 - Geracao de Memorial Descritivo
**Agente:** Mestre da Automacao + Agente RAG | **Ferramenta:** Jinja2 + ReportLab

O memorial deve conter:
- cabecalho com dados do proprietario e do imovel;
- tabela de vertices;
- descricao de confrontacoes;
- area total e perimetro calculados pela API;
- rodape com nome e CREA do responsavel tecnico.

**Criterio de aceitacao:** Gerar o memorial de um projeto real e submeter ao Agente RAG para validacao contra a Norma Tecnica para Georreferenciamento do INCRA.

---

## Agente RAG - Configuracao Obrigatoria

O `.cursorrules` menciona o Agente RAG mas nao define sua base de conhecimento. Sem documentos indexados, o agente e apenas um LLM generico sem autoridade legal.

**Documentos a indexar em `docs/normas/`:**

| Documento | Fonte |
|---|---|
| Norma Tecnica de Georreferenciamento de Imoveis Rurais (3a ed.) | INCRA |
| Manual Tecnico de Limites e Divisas | INCRA |
| Lei 13.465/2017 | Planalto.gov.br |
| Instrucao Normativa INCRA no 77/2013 | INCRA |
| Manual do SIGEF | INCRA |

**Configuracao no Cursor:** adicionar a pasta `docs/normas/` ao contexto do agente RAG.

---

## Orcamento Estimado de Infraestrutura

| Servico | Plano Gratuito | Quando pagar | Custo estimado |
|---|---|---|---|
| Supabase | 500MB banco, 2GB storage | >10 projetos ativos | ~US$ 25/mes |
| Expo / EAS Build | 30 builds/mes | Build iOS | ~US$ 29/mes |
| WhatsApp Business API | Primeiras 1000 msgs/mes gratis | Volume > 1000 | Variavel |
| Mapbox | 50.000 views/mes | App em producao | ~US$ 0.50/1000 views |
| AWS S3 | 5GB gratuito 12 meses | Apos trial | ~US$ 0.023/GB/mes |

**Conclusao:** O MVP roda no gratuito. Custos reais comecam quando o app tiver clientes ativos.

---

## Criterios de Avanco entre Fases

```text
Fase 0 -> Fase 1: gabarito matematico criado e aprovado por humano
Fase 1 -> Fase 2: app funciona offline, calculos passam 100% no pytest, app testado em campo
Fase 2 -> Fase 3: pelo menos 1 levantamento real completo feito com o app, exportacao DXF validada no Metrica TOPO
Fase 3 -> Producao: memorial validado pelo Agente RAG, portal testado por cliente real
```

---

## Regras para o Vibe Coding

1. Sempre comece pelo gabarito.
2. Agente certo para cada task.
3. Anexe sempre as imagens de referencia do LandStar quando pedir telas novas.
4. Um endpoint por vez.
5. Teste no celular fisico, nao so no simulador.
6. Nunca avance de fase sem os criterios de aceitacao satisfeitos.

---

*Master Plan v2 - GeoAdmin Pro | Ultima atualizacao: Marco 2026*
