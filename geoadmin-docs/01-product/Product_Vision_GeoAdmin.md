# 🗺️ GeoAdmin Pro (Projeto Desenrola)
**Sistema de Gestão e Automação para Regularização Fundiária Digital**

Este projeto une a coleta técnica de alta precisão (campo) com a gestão burocrática de escritório, utilizando uma arquitetura resiliente e automatizada para topógrafos.

---

## 🛠️ Stack Tecnológica
* **Mobile:** React Native + Expo (Foco em uso offline e campo).
* **Backend:** FastAPI (Python) para geoprocessamento pesado.
* **Banco de Dados:** Supabase com PostGIS (SIRGAS 2000 - SRID 4674).
* **Automação:** Pipeline via PowerShell/Python para integração com Métrica TOPO.

---

## 📂 Mapa de Documentação
Abaixo estão os guias mestres para o desenvolvimento e manutenção do sistema:

1. **[PRD_GeoAdmin.md](./PRD_GeoAdmin.md)**: Requisitos do produto, pilares do sistema e fórmulas matemáticas.
2. **[Master_Plan.md](./Master_Plan.md)**: Roadmap de desenvolvimento dividido em 3 fases (MVP, Gestão, Diferencial).
3. **[.cursorrules](./.cursorrules)**: Configuração dos 6 Agentes de IA para desenvolvimento via Cursor/Windsurf.
4. **[Comandos_Agentes.md](./Comandos_Agentes.md)**: Biblioteca com 150+ comandos prontos para UI, Engenharia, Automação, Dados, Auditoria e RAG.
5. **[Blindagem_Resiliencia.md](./Blindagem_Resiliencia.md)**: Mapa de tratamento de erros, resiliência e pipeline de testes.

---

## 🛡️ Resiliência e "Casca" (Error Handling)
Para evitar falhas em campo ou erros jurídicos no INCRA, o sistema segue estas regras fundamentais:
* **Validação de Topologia:** Nenhuma geometria é salva sem passar pelo `shape.is_valid` da Shapely.
* **Códigos de Erro:** Falhas matemáticas e de conexão possuem códigos específicos (001-999) para suporte rápido.
* **Pipeline Blindada:** Scripts de automação possuem *timeouts* e sistemas de *heartbeat* para evitar travamentos.
* **Redundância de Dados:** Sincronização offline-first para garantir que nenhum ponto coletado no campo seja perdido por falta de sinal.

---

## 🚀 Como Iniciar (Vibe Coding)
1. Certifique-se de que o arquivo `.cursorrules` está na raiz do projeto.
2. Abra o chat do seu editor (Cursor/Windsurf).
3. Ative o agente necessário no chat (ex: *"Agente Arquiteto UI/UX, crie a tela de ferramentas"*).
4. Siga rigorosamente o **Checklist de Validação de Matemática Geodésica** antes de qualquer deploy.

---
**Autor:** Hugo (Desenrola Team)
**Status:** Em Desenvolvimento (Fase 1)
