# Auditoria de Pastas de Trabalho

Data da auditoria: 2026-03-16
Origem auditada: `D:\pastas de trabalho`

## Resumo

A raiz `D:\pastas de trabalho` mistura:

- projetos reais de topografia/georreferenciamento;
- bases e jobs LandStar/TOPO;
- backups e pastas de apoio;
- materiais brutos, cursos, suporte e arquivos soltos.

Por isso, **nao e seguro importar a raiz inteira direto para `clientes` e `projetos`**.

## Sinais de projeto real encontrados

Pastas com combinacao forte de artefatos tipicos de projeto:

- `csv`, `kml`, `pdf`, `tbkp`, `topo`, `txt`
- ou combinacoes proximas disso

## Candidatos fortes para primeira leva

Essas pastas parecem bons candidatos para um import inicial controlado:

- `abadia`
- `bruno e luana`
- `campo 1812`
- `CH vitoria zildinha[`
- `colinas 040`
- `emerson e gabriel`
- `fazenda margarida`
- `indaia`
- `japo`
- `licinha e marcus`
- `MANGABA2`
- `pirinopolis`
- `samambaia`
- `teodora`
- `victor`

## Candidatos moderados

Podem virar projeto, mas precisam leitura de metadados antes:

- `amandas`
- `assentamento`
- `calito`
- `candido`
- `cristalina`
- `descriminatoria`
- `erejota`
- `escola pet`
- `fiorello`
- `gilson amorim`
- `jardimbotanico`
- `joana`
- `lago norte`
- `lauro`
- `lote ca`
- `nabil`
- `paracatuu`
- `renata parkway`
- `renato lago sul`
- `sidrolandia`
- `togim cartorio`
- `toguim`

## Pastas com alto risco de falso positivo

Estas aparentam ser backup, bruto, suporte ou mistura operacional:

- `AGUAS DA CHAPADA`
- `aguradando seleção`
- `backup0708`
- `brutos batimetria`
- `camera coletora`
- `certificado`
- `curvas de nivel`
- `dwg GUEM`
- `FINALIZAR`
- `Geoid`
- `install`
- `kml`
- `Nova Pasta`
- `Nova pasta (2)`
- `Suporte`
- `Temp`
- `Temporário`
- `TODOS OS PONTOS`

## Observacoes tecnicas

- Existem pastas com estrutura LandStar como `BaseMap`, `codes` e `gis`, por exemplo em `ALEXÂNIA`, `toguim` e `toguin`.
- Nem toda pasta com `BaseMap/codes/gis` tem metadado suficiente para inferir cliente e projeto automaticamente.
- O melhor import real deve cruzar nome da pasta com arquivos `pdf`, `csv`, `txt`, `kml` e eventualmente `numero_job`.

## Recomendacao

Executar em duas etapas:

1. `dry-run` de import somente dos candidatos fortes
2. validacao humana rapida da lista cliente/projeto antes de gravar no Supabase
