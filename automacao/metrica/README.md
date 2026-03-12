# Automacao real do Metrica TOPO

## Arquivos
- `run_metrica_real.ps1`: automacao de UI (abre o Metrica, abre projeto, envia comandos).
- `run_tudo_real.ps1`: orquestrador (UI + pos-processamento + checklist).
- `postprocess_gdal.ps1`: converte `.shp` em `.geojson`.
- `update_checklist.ps1`: marca itens no checklist de roteiro.
- `checklist_roteiro.md`: roteiro completo em formato executavel.
- `config.example.json`: configuracao base.
- `pontos.txt`: coordenadas usadas na `PL`.
- `lotes_exemplo.txt`: exemplo para multiplos lotes.

## Dashboard Web
- `ui/server.py`: API + frontend local.
- `ui/static/index.html`: tela principal.
- `start_ui.ps1`: comando unico para subir a interface.

Subir dashboard:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\Documents\Playground\automacao\metrica\start_ui.ps1"
```

Abrir no navegador:
- `http://127.0.0.1:8787`

## Multiplos lotes (novo)
No painel "Multiplos Lotes (Fila)", informe 1 projeto por linha e clique:
- `Rodar Lote Real` para executar de verdade.
- `Rodar Lote DryRun` para validar sem enviar teclas.

Comportamento:
- Processamento sequencial (um lote por vez).
- Cada lote gera config/runtime e logs em `automacao\metrica\batch_runs\<batch_id>\...`.
- Cada lote recebe sua propria copia de checklist.
- Pode parar o lote em andamento com `Parar Lote`.

## Execucao unica via script
Teste sem enviar teclas:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\Documents\Playground\automacao\metrica\run_tudo_real.ps1" -ConfigPath "C:\Users\User\Documents\Playground\automacao\metrica\config.json" -DryRun
```

Execucao real:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\Documents\Playground\automacao\metrica\run_tudo_real.ps1" -ConfigPath "C:\Users\User\Documents\Playground\automacao\metrica\config.json"
```

## Fluxo padrao atual
- Pre: `LISTAR`
- Desenho: `PL` + pontos do arquivo
- Finais: `WB`, `MEMORIAL`
