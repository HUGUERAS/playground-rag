# API Service

Backend principal do `GeoAdmin`.

## Stack inicial

- FastAPI
- Python
- deploy no Railway
- integracao com Supabase

## Primeiros endpoints

- `GET /health`
- `POST /geo/inverso`
- `POST /geo/area`
- `POST /geo/converter`

## Estrutura

- `app/main.py`: bootstrap do FastAPI.
- `app/api/routes`: endpoints HTTP.
- `app/services`: logica de negocio.
- `app/geo`: camada de compatibilidade para funcoes geodesicas legadas.
- `pyproject.toml`: dependencia e metadata para deploy.

## Backend oficial

O backend oficial do projeto e `C:\Users\User\Documents\Playground\services\api`.

O diretório legado `C:\Users\User\Documents\Playground\backend` foi descontinuado para evitar duplicidade de regra de negocio.

## Rodando localmente

```powershell
cd C:\Users\User\Documents\Playground\services\api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Configuracao de ambiente

Copie `.env.example` para `.env` e preencha:

- `GEOADMIN_SUPABASE_URL`
- `GEOADMIN_SUPABASE_KEY`

Se essas variaveis nao estiverem definidas, a API sobe normalmente, mas o healthcheck vai indicar que o Supabase ainda nao esta configurado.

## Arquivos de apoio

- `requirements.txt`: conjunto minimo de dependencias congeladas para instalar o backend em outra maquina.
- `pyproject.toml`: metadata e dependencias principais do servico.
- `C:\Users\User\Documents\Playground\scripts\import_project_points.py`: importador de pontos reais a partir de `KML`, `CSV` e `TXT` das pastas de trabalho ja mapeadas para projetos.

## Exemplo de payload

### `POST /geo/inverso`

```json
{
  "start": { "name": "P1", "x": 1000, "y": 2000 },
  "end": { "name": "P2", "x": 1010, "y": 2015 },
  "unit": "meters",
  "srid": 4674
}
```

### `POST /geo/converter`

```json
{
  "lat": -15.779167,
  "lon": -47.929722,
  "zona": "23S",
  "source_srid": 4674
}
```
