param(
    [Parameter(Mandatory = $true)]
    [string]$ZipPath,

    [Parameter(Mandatory = $false)]
    [string]$HtmlPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputRoot = "C:\Users\User\Documents\Playground\geoadmin-docs",

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$ingestScript = Join-Path $scriptDir "ingest_geoadmin.py"
$reviewScript = Join-Path $scriptDir "review_docs.py"

if (-not (Test-Path $ingestScript)) {
    throw "ingest script not found: $ingestScript"
}

if (-not (Test-Path $reviewScript)) {
    throw "review script not found: $reviewScript"
}

if (-not (Test-Path $ZipPath)) {
    throw "zip not found: $ZipPath"
}

if ($HtmlPath -and -not (Test-Path $HtmlPath)) {
    throw "html not found: $HtmlPath"
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    throw "python is not available on PATH"
}

$ingestArgs = @(
    $ingestScript,
    "--zip", $ZipPath,
    "--output", $OutputRoot
)

if ($HtmlPath) {
    $ingestArgs += @("--html", $HtmlPath)
}

if ($Overwrite) {
    $ingestArgs += "--overwrite"
}

Write-Host ""
Write-Host "== GeoAdmin ingest =="
& python @ingestArgs
if ($LASTEXITCODE -ne 0) {
    throw "ingest failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "== GeoAdmin review =="
& python $reviewScript "--root" $OutputRoot
if ($LASTEXITCODE -ne 0) {
    throw "review failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "GeoAdmin pipeline finished."
Write-Host "Docs root: $OutputRoot"
