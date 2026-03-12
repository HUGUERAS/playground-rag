[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ChecklistPath,
    [string[]]$DoneIds = @(),
    [string[]]$UndoIds = @(),
    [string]$Note = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ChecklistPath)) {
    throw "Checklist nao encontrado: $ChecklistPath"
}

$doneSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$undoSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

foreach ($id in $DoneIds) {
    if (-not [string]::IsNullOrWhiteSpace($id)) {
        [void]$doneSet.Add($id.Trim())
    }
}
foreach ($id in $UndoIds) {
    if (-not [string]::IsNullOrWhiteSpace($id)) {
        [void]$undoSet.Add($id.Trim())
    }
}

$lines = Get-Content -LiteralPath $ChecklistPath -Encoding UTF8
$changed = 0

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match '^- \[( |x)\] \[([A-Z0-9_]+)\] ') {
        $state = $matches[1]
        $id = $matches[2]

        $target = $state
        if ($doneSet.Contains($id)) { $target = 'x' }
        if ($undoSet.Contains($id)) { $target = ' ' }

        if ($target -ne $state) {
            $lines[$i] = $line -replace '^- \[( |x)\]', "- [$target]"
            $changed++
        }
    }
}

if (-not [string]::IsNullOrWhiteSpace($Note)) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $lines += "- $stamp - $Note"
    $changed++
}

if ($changed -gt 0) {
    Set-Content -LiteralPath $ChecklistPath -Value $lines -Encoding UTF8
}

Write-Host "Checklist atualizado: $ChecklistPath (alteracoes: $changed)"
