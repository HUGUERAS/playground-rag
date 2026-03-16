# Architecture and Deployment GeoAdmin

## Arquitetura recomendada agora

O `GeoAdmin` deve começar com uma arquitetura enxuta, usando os servicos que voce ja possui e deixando o `Google Cloud` para a fase em que houver carga real ou jobs mais pesados.

## Divisao de responsabilidade por plataforma

### Supabase

Usar como nucleo de dados e autenticacao.

- PostgreSQL principal do sistema.
- PostGIS para geometrias e consultas espaciais.
- Auth para topografo, equipe interna e cliente.
- Storage para documentos, imagens, DXF, PDFs e arquivos tecnicos.
- Policies de acesso por perfil.

### Railway

Usar como casa inicial do backend Python.

- API `FastAPI`.
- Calculos tecnicos como `Inverso`, `Area`, `Interseccao` e afins.
- Geracao de PDF, TXT e artefatos tecnicos.
- Automacoes Python de curta e media duracao.
- Jobs internos enquanto o volume ainda for pequeno.

### Vercel

Usar para superfícies web.

- Portal do cliente.
- Backoffice web administrativo.
- Landing, login e painel de acompanhamento.
- APIs web leves se forem simples e proximas da UI.

### GitHub

Usar como espinha dorsal de colaboracao e automacao.

- Repositorio do projeto.
- Pull requests e revisao.
- GitHub Actions para lint, testes e checagens documentais.
- Deploy automatizado quando a base estiver mais madura.

### Google Cloud

Reservar para a fase 2 ou 3, quando houver necessidade real.

- `Cloud Run` para workers ou API Python com mais controle.
- `Cloud Scheduler` para tarefas agendadas.
- `Pub/Sub` para filas.
- `Cloud Storage` se o storage tecnico crescer alem do confortavel no Supabase.

## O que vai em cada camada

### Dados principais no Supabase

- usuarios
- perfis
- projetos
- jobs
- pontos
- linhas
- superficies
- camadas
- codigos
- anexos e documentos
- historico de sincronizacao

### Logica de negocio no Railway

- validacao de entrada tecnica
- calculos geodesicos e geometricos
- geracao de memorial
- exportacao tecnica
- integracoes futuras com ferramentas externas

### Experiencia web no Vercel

- consulta de status do cliente
- upload de documentos
- painel de acompanhamento interno
- visualizacao de indicadores e listas

## O que nao colocar no Vercel no inicio

- processamento pesado de geometria
- jobs demorados
- geracao longa de PDF ou DXF
- pipelines de automacao tecnica

## Criterio para migrar parte do backend para Google Cloud

Migrar quando um destes sinais aparecer:

- jobs tecnicos demorados comecarem a falhar ou escalar mal no Railway;
- processamento assíncrono ficar necessario;
- o custo operacional do Railway deixar de compensar;
- houver necessidade de fila, scheduler ou workers dedicados.
