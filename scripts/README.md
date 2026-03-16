# Scripts GeoAdmin

## Objetivo

Estes scripts ajudam a manter a documentacao do `GeoAdmin` barata de operar: o processamento mecanico fica no Python, e a IA entra apenas para revisao e refinamento.

## Scripts

### `run_geoadmin.ps1`

Encadeia ingestao e revisao em um unico comando.

Exemplo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_geoadmin.ps1 `
  -ZipPath "C:\Users\User\Downloads\Como organizar o conteúdo do arquivo_.zip" `
  -HtmlPath "C:\Users\User\Downloads\Google Gemini.html" `
  -OutputRoot "C:\Users\User\Documents\Playground\geoadmin-docs" `
  -Overwrite
```

### `ingest_geoadmin.py`

Recebe o `.zip` oficial e, opcionalmente, o `Google Gemini.html`, depois:

- cria a estrutura `geoadmin-docs`;
- promove os documentos do pacote para caminhos padronizados;
- arquiva os arquivos brutos em `05-source-archive`;
- gera um `Source_Index.md`.

Exemplo:

```powershell
python scripts/ingest_geoadmin.py `
  --zip "C:\Users\User\Downloads\Como organizar o conteúdo do arquivo_.zip" `
  --html "C:\Users\User\Downloads\Google Gemini.html" `
  --output "C:\Users\User\Documents\Playground\geoadmin-docs" `
  --overwrite
```

### `review_docs.py`

Faz uma revisao leve da arvore documental:

- valida arquivos esperados;
- detecta headings duplicados;
- aponta markdowns vazios;
- checa se o mapeamento funcional cobre as areas-chave;
- lista arquivos com gaps e pendencias.

Exemplo:

```powershell
python scripts/review_docs.py --root "C:\Users\User\Documents\Playground\geoadmin-docs"
```

## Fluxo recomendado

1. Rode `run_geoadmin.ps1` para atualizar a base.
2. Leia o resumo do `review_docs.py`.
3. So depois envie arquivos pequenos para IA usando os prompts da pasta `prompts/`.
