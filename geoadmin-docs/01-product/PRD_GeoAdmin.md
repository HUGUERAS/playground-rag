# PRD: Sistema GeoAdmin (Projeto Desenrola)

## 1. Objetivo do Produto
Profissionalizar e digitalizar o processo de regularização fundiária no Brasil. O sistema integra a coleta técnica de alta precisão no campo com a gestão administrativa e o atendimento ao cliente.

## 2. Pilares do Sistema
* **Módulo de Campo:** Focado em precisão, coleta de pontos GNSS e cálculos rápidos.
* **Módulo Backoffice:** Gestão de status de processos, financeiro e controle de prazos.
* **Módulo do Cliente:** Portal de transparência com upload de documentos e status via Magic Link.

## 3. Requisitos Técnicos e Stack
* **Mobile:** React Native (Expo).
* **Backend:** FastAPI (Python) para cálculos e automação.
* **Banco de Dados:** Supabase com extensão PostGIS (SRID 4674 - SIRGAS 2000).
* **Cálculos Geométricos:** Uso obrigatório das bibliotecas **Shapely** e **Pyproj**.

## 4. Fórmulas de Referência
Para o cálculo de **Inverso**:
* ΔX = X₂ - X₁
* ΔY = Y₂ - Y₁
* Distância = √(ΔX² + ΔY²)
* Azimute = arctan2(ΔX, ΔY)

## 5. Fluxos de Autenticação
* **Topógrafo:** Login completo com e-mail/senha.
* **Cliente:** Acesso via link mágico enviado por WhatsApp/E-mail para preenchimento de dados e acompanhamento.

## 6. Resiliência e Blindagem (Casca)
* **Validação de Topologia:** Nenhuma geometria é salva sem passar pelo `shape.is_valid` da Shapely.
* **Códigos de Erro:** Falhas matemáticas e de conexão possuem códigos específicos (001-999) para suporte rápido.
* **Pipeline Blindada:** Scripts de automação possuem *timeouts* e sistemas de *heartbeat* para evitar travamentos.
* **Redundância de Dados:** Sincronização offline-first para garantir que nenhum ponto coletado no campo seja perdido por falta de sinal.
