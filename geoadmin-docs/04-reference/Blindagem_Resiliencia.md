# Blindagem e Resiliência (Error Handling) - GeoAdmin Pro

Este documento detalha as estratégias de tratamento de erros e a pipeline de testes para garantir que o sistema seja um "tanque de guerra" em campo.

## 🛡️ 1. O Mapa de "Casca": Onde o Código Quebra

| Ponto de Falha | Risco | Mensagem de Erro Específica | Ação de Resiliência |
| :--- | :--- | :--- | :--- |
| Cálculo de Inverso | Divisão por zero (ΔY=0) | `ERR_MATH_001`: Pontos idênticos. Impossível calcular azimute. | Bloquear cálculo; exigir distância > 0. |
| Geometria | Polígono Aberto/Cruzado | `ERR_GEOM_002`: Topologia inválida. Verifique linhas cruzadas. | Validação automática via Shapely antes do save. |
| Sincronização | Sem Internet no Campo | `WARN_SYNC_003`: Offline. Dados salvos localmente no cache. | Sincronização em background automática. |
| Automação | Métrica TOPO travou | `ERR_AUTO_004`: Timeout no Métrica TOPO. Reiniciando pipeline... | Sistema de Heartbeat e Retry automático. |
| Segurança | Tentativa de invasão (RLS) | `ERR_AUTH_005`: Acesso negado. Tentativa registrada para auditoria. | Bloqueio imediato da sessão e log no Supabase. |

## 🧪 2. Pipeline de Testes por Etapa

### Etapa 1: Testes Unitários (A Matemática)
* **Foco:** Validar cada função da Shapely e Pyproj.
* **Cenário Crítico:** Testar cálculos no limite das zonas UTM (Zona 22S vs 23S).
* **Ferramenta:** `pytest` no Python.

### Etapa 2: Testes de Integração (O Fluxo de Dados)
* **Foco:** Validar se o App consegue ler o que o Supabase escreveu.
* **Cenário Crítico:** Simular queda de conexão durante o upload de um DXF pesado.
* **Ferramenta:** Postman / Insomnia.

### Etapa 3: Testes E2E (A Automação)
* **Foco:** Validar o caminho completo: App -> API -> PowerShell -> Métrica TOPO -> PDF Final.
* **Cenário Crítico:** Inserir dados propositalmente errados para ver se o sistema trava ou reporta o erro corretamente.

## 🤖 3. Comandos de Auditoria (Para o Agente Revisor)
1. Revise todos os blocos `try/except` e substitua erros genéricos por códigos específicos de 001 a 999.
2. Simule uma falha de banco de dados e verifique se o sistema faz o rollback da transação corretamente.
3. Verifique se o app mobile tem um "State Manager" que recupera o progresso caso o app seja fechado.
4. Analise a redundância dos backups: se o servidor da API cair, onde os dados de campo ficam salvos?
5. Implemente um validador de "Input Sanity" para impedir que nomes de projetos tenham caracteres especiais (#, &, %).
