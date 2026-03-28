# Master Plan: Estratégia de Desenvolvimento GeoAdmin

Este documento detalha o roteiro de desenvolvimento do sistema GeoAdmin, dividido em três fases principais para garantir uma evolução sustentável e focada no MVP.

## Fase 1: Inteligência e Núcleo (MVP)
Nesta etapa inicial, o foco está em garantir a precisão matemática dos cálculos e a integridade da base de dados.

| Task ID | Descrição | Ferramenta |
| :--- | :--- | :--- |
| 1.1 | Configurar Supabase com tabelas de projetos e lotes. | Supabase / PostGIS |
| 1.2 | Implementar API de cálculos (Inverso e Área) usando Shapely. | FastAPI / Python |
| 1.3 | Adaptar script `gerador_topo.py` para serviço de nuvem. | Python |

## Fase 2: Interface e Campo
O objetivo aqui é criar a ferramenta de uso diário do topógrafo, priorizando a usabilidade e o funcionamento offline.

| Task ID | Descrição | Ferramenta |
| :--- | :--- | :--- |
| 2.1 | Criar Dashboard mobile com a grade 3x6 de ferramentas. | React Native / Expo |
| 2.2 | Implementar visualização de mapa SIRGAS 2000. | Mapbox / Leaflet |
| 2.3 | Criar sistema de coleta e salvamento de pontos offline. | SQLite / WatermelonDB |

## Fase 3: Administrativo e Cliente
A fase final foca na facilitação da entrega dos serviços e na melhoria da comunicação com o cliente final.

| Task ID | Descrição | Ferramenta |
| :--- | :--- | :--- |
| 3.1 | Lançar o portal do cliente para upload de documentos (RG, Escritura). | React Native / Magic Link |
| 3.2 | Gerar Memorial Descritivo automático em PDF/TXT. | ReportLab / Jinja2 |
| 3.3 | Integrar notificações automáticas de status via WhatsApp. | Twilio / WhatsApp API |

## Próximos Passos
1. Iniciar o Setup do Supabase (Task 1.1).
2. Validar o primeiro cálculo de área via API.
3. Integrar o RAG para conformidade legal (Lei 13.465/2017).
