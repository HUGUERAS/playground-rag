# Biblioteca de Comandos (Prompt Dictionary) - GeoAdmin Pro

Este documento contém uma lista de comandos prontos para serem usados com os agentes de IA no Cursor ou Windsurf.

## 🎨 1. Agente Arquiteto UI/UX (O Visual)
1. Crie a tela inicial com navegação inferior de 4 abas.
2. Gere a grade 3x6 de ferramentas com ícones laranjas (#FF9500).
3. Implemente o "Modo de Alta Claridade" para uso sob sol forte.
4. Crie o formulário de "Novo Projeto" com campos para zona UTM.
5. Construa a lista de pontos com badges de status coloridos.
6. Crie um canvas de desenho estilo CAD para plotagem de pontos.
7. Implemente a tela de configurações de unidades (Metros/Pés).
8. Desenhe a landing page do "Magic Link" para o cliente final.
9. Crie um seletor de arquivos para importar CSV e DXF.
10. Construa o card de resultado de cálculo com botão de exportar.
11. Implemente o modal de seleção de sistema SIRGAS 2000.
12. Crie a interface específica para a ferramenta "Subdivisão de Área".
13. Implemente um tema escuro para economia de bateria no campo.
14. Crie a tela de perfil do proprietário para gestão de documentos.
15. Adicione um indicador de status de sinal GNSS em tempo real.
16. Construa a galeria de vídeos de ajuda e tutoriais.
17. Desenhe o formulário de entrada para a função "Inverso".
18. Implemente uma barra de progresso para sincronização com a nuvem.
19. Crie um botão flutuante para salvar pontos rapidamente.
20. Desenhe a gaveta lateral de seleção de camadas (Layers).
21. Crie a tela de erro para "Acesso Restrito/Assinatura".
22. Construa a visualização hierárquica de pastas e jobs.
23. Aplique fontes grandes e botões táteis para uso com luvas.
24. Crie o prompt visual para cálculo de "Ponto Tangente".
25. Implemente a lista de "Histórico de Cálculos" recentes.
26. Adicione um botão de compartilhamento de status via WhatsApp.
27. Construa a interface de backup e restauração de projetos.
28. Crie um slider/input para conversão angular rápida.
29. Desenhe o painel de controle para "Ajuste do Mapa".
30. Crie o dashboard simplificado para a visão do cliente.

## 📐 2. Agente Engenheiro Geográfico (A Matemática)
1. Implemente o cálculo de "Inverso" entre dois pontos.
2. Crie o endpoint de cálculo de "Área" usando Shapely.
3. Crie a função de conversão SIRGAS 2000 para WGS84.
4. Implemente a matemática de "Distância Ponto a Linha".
5. Crie a função para encontrar a intersecção de duas linhas.
6. Implemente a rotação de pontos baseada em um centro.
7. Crie o calculador de ângulo de bissecção.
8. Implemente o cálculo de média de pontos (Centroide).
9. Construa o módulo de ajuste por Mínimos Quadrados.
10. Crie o endpoint para cálculo de volume de pilhas de terra.
11. Implemente a validação de polígonos auto-interseccionados.
12. Formate a precisão decimal das coordenadas para 6 casas.
13. Crie la lógica de transformações para a Zona UTM 23S.
14. Implemente o cálculo de ângulos de deflexão.
15. Construa o resolvedor geométrico para "Ponto Tangente".
16. Crie o parser para leitura de sentenças NMEA do GNSS.
17. Implemente a matriz de transformação de coordenadas.
18. Desenvolva o serviço de verificação se ponto está dentro do lote.
19. Crie o endpoint para calcular o perímetro total do polígono.
20. Implemente o cálculo de distância geodésica para linhas longas.
21. Construa o logger de histórico de operações matemáticas.
22. Crie la função de "Buffer" para criar áreas de servidão.
23. Implemente a divisão de linhas por distância fixa.
24. Crie a conversão de Graus/Min/Seg para Decimal e vice-versa.
25. Implemente o formatador de Rumos (NE, SE, SW, NW).
26. Crie o calculador de inclinação e rampa.
27. Adicione validação para evitar pontos duplicados no lote.
28. Crie o endpoint para obter a cota média do terreno.
29. Implemente a lógica de "Offset" lateral de pontos.
30. Gere a saída de coordenadas formatada para KML (WGS84).

## 🤖 3. Agente Mestre da Automação (O Pipeline)
1. Adapte o gerador_topo.py para receber dados via API.
2. Crie a função para gerar arquivos DXF com a ezdxf.
3. Implemente a troca de placeholders em Memoriais Descritivos.
4. Crie script PowerShell para abrir projetos no Métrica TOPO.
5. Implemente script AutoHotKey para importação em lote.
6. Gere o Memorial Descritivo em formato PDF profissional.
7. Crie um monitor de status para tarefas em segundo plano.
8. Colete logs de erro das execuções do PowerShell.
9. Implemente o pipeline de exportação para KML do Google Earth.
10. Construa o conversor automatizado de CSV para DXF.
11. Crie um carregador de templates para diferentes prefeituras.
12. Implemente o disparador de mensagens de status via WhatsApp.
13. Crie o script de backup automático para o Google Drive.
14. Implemente a limpeza automática de arquivos temporários de cálculo.
15. Construa o mapeador de camadas (Layers) para o DXF final.
16. Crie um "Wrapper" para rodar comandos do Métrica TOPO via CLI.
17. Automatize a criação da estrutura de pastas de novos clientes.
18. Gere relatórios técnicos baseados nos logs de cálculos.
19. Implemente recuperação de erros para falhas na automação.
20. Crie um empacotador ZIP com todos os arquivos finais do job.
21. Integre uma ponte para assinatura digital de documentos.
22. Envie e-mail automático para o escritório ao finalizar job.
23. Crie o importador de dados do formato SIGEF/INCRA.
24. Implemente o calculador automático de escala para plotagem.
25. Formate a lista de coordenadas em tabelas para o PDF.
26. Extraia metadados de arquivos DXF enviados pelo cliente.
27. Gere o QR Code de acesso exclusivo para o proprietário.
28. Sincronize dados entre o app móvel e o software desktop.
29. Crie um validador de sanidade para arquivos CSV de coletora.
30. Implemente o verificador de atualizações para os scripts locais.

## ☁️ 4. Agente Arquiteto de Dados (O Banco)
1. Defina a tabela projetos com políticas de segurança RLS.
2. Crie a tabela pontos com suporte a geometria PostGIS.
3. Configure a tabela clientes para acesso via Magic Link.
4. Implemente a função RPC buscar_vizinhos_adjacentes.
5. Crie a tabela lotes com suporte a polígonos complexos.
6. Implemente uma função SQL para checar topologia de lotes.
7. Crie uma "View" para resumo financeiro de orçamentos.
8. Implemente logs de auditoria para cada alteração no projeto.
9. Configure a expiração automática de tokens de acesso.
10. Crie a tabela de referência de Sistemas de Coordenadas.
11. Implemente o cálculo de área nativo direto no banco de dados.
12. Configure buckets no Storage para documentos dos clientes.
13. Defina as "Roles" de usuário (Topógrafo, Auxiliar, Cliente).
14. Crie consulta para detectar sobreposição ilegal entre lotes.
15. Ative o Realtime do Supabase para o status do processo.
16. Crie a visão consolidada para o dashboard do cliente.
17. Implemente a tabela de histórico de importações de arquivos.
18. Crie função para converter geometria PostGIS em GeoJSON.
19. Configure a política de retenção e backup do banco.
20. Crie índices espaciais para busca rápida por proximidade.
21. Vincule documentos físicos a IDs de projetos específicos.
22. Crie campo JSONB para metadados customizados de cada job.
23. Configure a projeção padrão SIRGAS 2000 UTM Zone 23S.
24. Implemente função SQL de distância entre pontos.
25. Crie rastreador de pendências de documentos do cliente.
26. Gere relatório de produtividade por topógrafo via SQL.
27. Proteja dados sensíveis do cliente com criptografia em nível de campo.
28. Crie índices para renderização veloz de mapas no mobile.
29. Implemente o sistema de atribuição de tarefas por projeto.
30. Aplique política de "Exclusão Lógica" (Soft Delete) para segurança.

## 🛡️ 5. Agente Revisor (O Auditor)
1. Revise as políticas de RLS da tabela lotes para evitar vazamento de dados.
2. Faça um "Stress Test" na API de cálculo de área com polígonos de 10.000 vértices.
3. Verifique se há vulnerabilidades de SQL Injection nas chamadas RPC do Supabase.
4. Analise o tratamento de erros na conexão Bluetooth com o GNSS.
5. Revise o script gerador_topo.py em busca de caminhos de arquivo (paths) vulneráveis.
6. Teste a integração do "Magic Link": ele expira corretamente após o uso?
7. Verifique se as coordenadas enviadas pelo mobile são validadas antes de entrar no banco.
8. Analise a performance da busca de vizinhos (PostGIS) em grandes bases de dados.
9. Encontre redundâncias de código entre o frontend web e o mobile.
10. Revise a segurança da chave de API do Supabase no código client-side.
11. Verifique se o cálculo de "Inverso" lida corretamente com pontos idênticos (divisão por zero).
12. Analise o consumo de memória do app ao carregar mapas pesados.
13. Valide se os placeholders dos Memoriais Descritivos são limpos contra scripts (XSS).
14. Verifique se a exportação em DXF gera arquivos corrompidos em casos extremos.
15. Revise a lógica de sincronização offline: há risco de sobrescrever dados mais novos?
16. Teste a precisão da conversão SIRGAS 2000 comparando com o software do IBGE.
17. Identifique dependências (bibliotecas) desatualizadas com vulnerabilidades conhecidas.
18. Verifique se há dados sensíveis (tokens) sendo salvos nos logs do console.
19. Analise a latência da API ao ser acessada via 4G/5G em áreas rurais.
20. Revise as permissões do app (Câmera, GPS, Arquivos) e remova as desnecessárias.
21. Teste se o sistema bloqueia corretamente o acesso após a expiração da assinatura.
22. Verifique se o upload de documentos do cliente aceita apenas formatos seguros (PDF/JPG).
23. Analise se o hash de senhas utiliza algoritmos modernos (Bcrypt/Argon2).
24. Revise a comunicação PowerShell/Python: os comandos são sanitizados?.
25. Verifique se o banco de dados tem índices espaciais suficientes para a escala do projeto.
26. Teste a visualização CAD em telas pequenas (smartphones antigos).
27. Identifique possíveis gargalos na geração simultânea de múltiplos memoriais.
28. Verifique se as unidades de medida (metros/pés) são consistentes em todo o fluxo.
29. Revise a documentação da API: todos os campos estão descritos corretamente?
30. Simule um ataque de força bruta no login e sugira mecanismos de bloqueio.

## 📚 6. Agente de Conhecimento (RAG)
1. "IA, este polígono atende aos requisitos de precisão do INCRA para áreas rurais?" (Consulta norma técnica).
2. "Gere uma cláusula de confrontação para este memorial baseada no último modelo de cartório de Brasília."
3. "Quais documentos o cliente ainda precisa enviar para este tipo de regularização?" (Consulta Lei 13.465).
4. "Explique a diferença técnica entre o SIGEF e o INCRA para este projeto."
5. "Valide se a redação deste memorial descritivo segue os padrões da ABNT."
