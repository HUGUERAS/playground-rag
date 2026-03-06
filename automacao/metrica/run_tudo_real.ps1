[CmdletBinding()]
param(
    [string]$ConfigPath = "$PSScriptRoot\config.json",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Arquivo nao encontrado: $ConfigPath"
}

$cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json

$uiScript = Join-Path $PSScriptRoot "run_metrica_real.ps1"
$postScript = Join-Path $PSScriptRoot "postprocess_gdal.ps1"
$checkScript = Join-Path $PSScriptRoot "update_checklist.ps1"

function Resolve-ChecklistPath {
    param($Config)

    $defaultPath = Join-Path $PSScriptRoot "checklist_roteiro.md"

    if (-not $Config.Checklist) {
        return [pscustomobject]@{ Enabled = $true; Path = $defaultPath }
    }

    $enabled = $true
    if ($Config.Checklist.PSObject.Properties.Name -contains 'Enabled') {
        $enabled = [bool]$Config.Checklist.Enabled
    }

    $path = $defaultPath
    if (($Config.Checklist.PSObject.Properties.Name -contains 'Path') -and -not [string]::IsNullOrWhiteSpace([string]$Config.Checklist.Path)) {
        $path = [string]$Config.Checklist.Path
    }

    return [pscustomobject]@{ Enabled = $enabled; Path = $path }
}

function Update-Checklist {
    param(
        [Parameter(Mandatory = $true)][string]$ChecklistPath,
        [string[]]$DoneIds = @(),
        [string[]]$UndoIds = @(),
        [string]$Note = ""
    )

    if (-not (Test-Path -LiteralPath $checkScript)) {
        Write-Host "Aviso: update_checklist.ps1 nao encontrado."
        return
    }

    & $checkScript -ChecklistPath $ChecklistPath -DoneIds $DoneIds -UndoIds $UndoIds -Note $Note
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao atualizar checklist."
    }
}

$cl = Resolve-ChecklistPath -Config $cfg

if ($cl.Enabled -and -not (Test-Path -LiteralPath $cl.Path)) {
    throw "Checklist habilitado, mas arquivo nao existe: $($cl.Path)"
}

if ($DryRun) {
    Write-Host "Modo DryRun: checklist nao sera marcado como concluido."
}

Write-Host "[1/2] Executando fluxo do Metrica..."
& $uiScript -ConfigPath $ConfigPath -DryRun:$DryRun
if ($LASTEXITCODE -ne 0) {
    if ($cl.Enabled) {
        Update-Checklist -ChecklistPath $cl.Path -Note "Erro no fluxo UI do Metrica"
    }
    throw "Fluxo do Metrica terminou com erro."
}

if ($cl.Enabled) {
    if ($DryRun) {
        Update-Checklist -ChecklistPath $cl.Path -Note "DryRun executado (nenhuma tecla enviada)"
    }
    else {
        Update-Checklist -ChecklistPath $cl.Path -DoneIds @("AUTO_1", "AUTO_2", "AUTO_3", "AUTO_4") -Note "Fluxo UI executado com sucesso"
    }
}

if ($DryRun) {
    Write-Host "DryRun ativo: pos-processamento nao executado."
    exit 0
}

if ($cfg.PostProcess.Enabled -eq $true) {
    Write-Host "[2/2] Executando pos-processamento GDAL..."
    & $postScript -InputDir ([string]$cfg.PostProcess.InputDir) -OutputDir ([string]$cfg.PostProcess.OutputDir) -Ogr2OgrExe ([string]$cfg.PostProcess.Ogr2OgrExe)
    if ($LASTEXITCODE -ne 0) {
        if ($cl.Enabled) {
            Update-Checklist -ChecklistPath $cl.Path -Note "Erro no pos-processamento GDAL"
        }
        throw "Pos-processamento retornou erro."
    }

    if ($cl.Enabled) {
        Update-Checklist -ChecklistPath $cl.Path -DoneIds @("AUTO_5") -Note "Pos-processamento GDAL concluido"
    }
}
else {
    Write-Host "[2/2] Pos-processamento desativado em config.json"
}

Write-Host "Fluxo completo finalizado."
