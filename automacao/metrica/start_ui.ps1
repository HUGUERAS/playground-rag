[CmdletBinding()]
param(
    [int]$Port = 8787,
    [string]$Host = "127.0.0.1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$server = Join-Path $PSScriptRoot "ui\server.py"
if (-not (Test-Path -LiteralPath $server)) {
    throw "Arquivo nao encontrado: $server"
}

Write-Host "Iniciando UI em http://$Host:$Port"
Set-Location -LiteralPath (Join-Path $PSScriptRoot "ui")
python .\server.py --host $Host --port $Port
