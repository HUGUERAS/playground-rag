[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$InputDir,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$Ogr2OgrExe = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Find-FirstFile {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$Filter,
        [int]$MaxDepth = 7
    )

    if (-not (Test-Path -LiteralPath $BasePath)) {
        return $null
    }

    $queue = [System.Collections.Generic.Queue[object]]::new()
    $queue.Enqueue([pscustomobject]@{ Path = $BasePath; Depth = 0 })

    while ($queue.Count -gt 0) {
        $item = $queue.Dequeue()
        $dir = [string]$item.Path
        $depth = [int]$item.Depth

        $hit = Get-ChildItem -LiteralPath $dir -File -Filter $Filter -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($hit) { return $hit.FullName }

        if ($depth -lt $MaxDepth) {
            $subs = Get-ChildItem -LiteralPath $dir -Directory -ErrorAction SilentlyContinue
            foreach ($sub in $subs) {
                $queue.Enqueue([pscustomobject]@{ Path = $sub.FullName; Depth = ($depth + 1) })
            }
        }
    }

    return $null
}

if ([string]::IsNullOrWhiteSpace($Ogr2OgrExe) -or -not (Test-Path -LiteralPath $Ogr2OgrExe)) {
    $Ogr2OgrExe = Find-FirstFile -BasePath "C:\Program Files (x86)" -Filter "ogr2ogr.exe" -MaxDepth 8
}
if (-not $Ogr2OgrExe) {
    throw "ogr2ogr.exe não encontrado automaticamente."
}
if (-not (Test-Path -LiteralPath $InputDir)) {
    throw "Pasta de entrada não encontrada: $InputDir"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$files = Get-ChildItem -LiteralPath $InputDir -Filter *.shp -File -ErrorAction SilentlyContinue
if (-not $files) {
    Write-Host "Nenhum .shp encontrado em $InputDir"
    exit 0
}

foreach ($f in $files) {
    $dest = Join-Path $OutputDir ($f.BaseName + ".geojson")
    Write-Host "Convertendo: $($f.Name) -> $dest"
    & $Ogr2OgrExe -f "GeoJSON" $dest $f.FullName
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na conversão de $($f.FullName)"
    }
}

Write-Host "Pós-processamento concluído."
