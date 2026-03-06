[CmdletBinding()]
param(
    [string]$ConfigPath = "$PSScriptRoot\config.json",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$stamp][$Level] $Message"
    Write-Host $line
    Add-Content -LiteralPath $script:LogPath -Value $line -Encoding UTF8
}

function Escape-SendKeys {
    param([string]$Text)
    return ($Text -replace '([+^%~(){}\[\]])', '{$1}')
}

function Send-Keys {
    param(
        [Parameter(Mandatory = $true)][string]$Keys,
        [int]$DelayMs = 250
    )

    if ($DryRun) {
        Write-Log "DRYRUN SendKeys: $Keys"
    }
    else {
        $script:Wsh.SendKeys($Keys)
    }
    Start-Sleep -Milliseconds $DelayMs
}

function Send-TextAndEnter {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [int]$AfterMs = 500
    )

    $escaped = Escape-SendKeys -Text $Text
    Send-Keys -Keys $escaped -DelayMs 120
    Send-Keys -Keys "~" -DelayMs $AfterMs
}

function Wait-AppActivate {
    param(
        [Parameter(Mandatory = $true)][string]$Target,
        [int]$TimeoutSec = 30
    )

    if ($DryRun) {
        Write-Log "DRYRUN Activate: $Target"
        return $true
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if ($script:Wsh.AppActivate($Target)) {
            Start-Sleep -Milliseconds 300
            return $true
        }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

function Wait-ProcessMainWindow {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [int]$TimeoutSec = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $Process.Refresh()
        if ($Process.MainWindowHandle -ne 0) {
            return $true
        }
        Start-Sleep -Milliseconds 300
    }
    return $false
}

function Find-FirstFile {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$Filter,
        [int]$MaxDepth = 5
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
        if ($hit) {
            return $hit.FullName
        }

        if ($depth -lt $MaxDepth) {
            $subs = Get-ChildItem -LiteralPath $dir -Directory -ErrorAction SilentlyContinue
            foreach ($sub in $subs) {
                $queue.Enqueue([pscustomobject]@{ Path = $sub.FullName; Depth = ($depth + 1) })
            }
        }
    }

    return $null
}

function Resolve-MetricaExePath {
    param([string]$ConfiguredPath)

    if ($ConfiguredPath -and (Test-Path -LiteralPath $ConfiguredPath)) {
        return $ConfiguredPath
    }

    $found = Find-FirstFile -BasePath "C:\Program Files (x86)" -Filter "Metrica_TOPO_CAD.exe" -MaxDepth 6
    return $found
}

function Resolve-Config {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Arquivo de configuração não encontrado: $Path"
    }

    $cfg = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json

    if (-not $cfg.ProjectPath) { throw "Config inválida: ProjectPath é obrigatório." }
    if (-not $cfg.PointsFile) { throw "Config inválida: PointsFile é obrigatório." }

    if (-not $cfg.WindowTitleHint) { $cfg | Add-Member -NotePropertyName WindowTitleHint -NotePropertyValue "Metrica TOPO" }
    if (-not $cfg.OpenDialogTitles) { $cfg | Add-Member -NotePropertyName OpenDialogTitles -NotePropertyValue @("Abrir", "Open") }
    if (-not $cfg.Timing) {
        $cfg | Add-Member -NotePropertyName Timing -NotePropertyValue ([pscustomobject]@{
                AfterStartMs      = 3000
                AfterOpenDialogMs = 1200
                BetweenPointMs    = 180
                AfterCommandMs    = 700
            })
    }
    if (-not $cfg.PreCommands) { $cfg | Add-Member -NotePropertyName PreCommands -NotePropertyValue @("LISTAR") }
    if (-not $cfg.PostCommands) { $cfg | Add-Member -NotePropertyName PostCommands -NotePropertyValue @("WB", "MEMORIAL") }
    if (-not $cfg.LogDir) { $cfg | Add-Member -NotePropertyName LogDir -NotePropertyValue "$PSScriptRoot\logs" }

    $resolvedExe = Resolve-MetricaExePath -ConfiguredPath ([string]$cfg.MetricaExe)
    if (-not $resolvedExe) {
        throw "Não foi possível localizar Metrica_TOPO_CAD.exe automaticamente."
    }

    if ($cfg.PSObject.Properties.Name -contains 'MetricaExe') {
        $cfg.MetricaExe = $resolvedExe
    }
    else {
        $cfg | Add-Member -NotePropertyName MetricaExe -NotePropertyValue $resolvedExe
    }

    return $cfg
}

function Read-Points {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Arquivo de pontos não encontrado: $Path"
    }

    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    $points = @()
    foreach ($line in $lines) {
        $v = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($v)) { continue }
        if ($v.StartsWith("#") -or $v.StartsWith(";")) { continue }
        $points += $v
    }

    if ($points.Count -lt 2) {
        throw "Pontos insuficientes em $Path. Informe pelo menos 2 coordenadas."
    }

    return $points
}

$cfg = Resolve-Config -Path $ConfigPath

if (-not (Test-Path -LiteralPath $cfg.MetricaExe)) {
    throw "Executável do Métrica não encontrado: $($cfg.MetricaExe)"
}
if (-not (Test-Path -LiteralPath $cfg.ProjectPath)) {
    throw "Projeto não encontrado: $($cfg.ProjectPath)"
}

New-Item -ItemType Directory -Force -Path $cfg.LogDir | Out-Null
$script:LogPath = Join-Path $cfg.LogDir ("metrica_automation_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

try {
    $points = Read-Points -Path $cfg.PointsFile
    Write-Log "Pontos carregados: $($points.Count)"
    Write-Log "Projeto: $($cfg.ProjectPath)"
    Write-Log "Executável: $($cfg.MetricaExe)"

    $script:Wsh = New-Object -ComObject WScript.Shell

    if ($DryRun) {
        Write-Log "Modo DRYRUN ativo. Nenhuma tecla será enviada."
        Write-Log "Sequência: abrir app > abrir projeto > pre-commands > PL com pontos > post-commands"
        exit 0
    }

    $proc = Start-Process -FilePath $cfg.MetricaExe -PassThru
    Write-Log "Métrica iniciado. PID=$($proc.Id)"

    if (-not (Wait-ProcessMainWindow -Process $proc -TimeoutSec 60)) {
        throw "Janela principal não apareceu no tempo esperado."
    }

    if (-not (Wait-AppActivate -Target ([string]$proc.Id) -TimeoutSec 15)) {
        if (-not (Wait-AppActivate -Target $cfg.WindowTitleHint -TimeoutSec 15)) {
            throw "Não foi possível ativar a janela do Métrica."
        }
    }

    Start-Sleep -Milliseconds ([int]$cfg.Timing.AfterStartMs)
    Write-Log "Janela ativa. Abrindo projeto."

    Send-Keys -Keys "^o" -DelayMs 800

    $openActivated = $false
    foreach ($title in $cfg.OpenDialogTitles) {
        if (Wait-AppActivate -Target $title -TimeoutSec 3) {
            $openActivated = $true
            break
        }
    }
    if (-not $openActivated) {
        Write-Log "Diálogo de abertura não confirmado por título. Tentando digitação direta." "WARN"
    }

    Start-Sleep -Milliseconds ([int]$cfg.Timing.AfterOpenDialogMs)
    Send-TextAndEnter -Text ([string]$cfg.ProjectPath) -AfterMs 1200

    if (-not (Wait-AppActivate -Target ([string]$proc.Id) -TimeoutSec 20)) {
        if (-not (Wait-AppActivate -Target $cfg.WindowTitleHint -TimeoutSec 20)) {
            throw "A janela do Métrica não retornou após abrir projeto."
        }
    }

    Start-Sleep -Milliseconds 1200
    Write-Log "Projeto enviado para abertura. Iniciando comandos."

    foreach ($command in $cfg.PreCommands) {
        $cmd = [string]$command
        Write-Log "Comando prévio: $cmd"
        Send-TextAndEnter -Text $cmd -AfterMs ([int]$cfg.Timing.AfterCommandMs)
        Send-Keys -Keys "{ESC}" -DelayMs 300
    }

    Write-Log "Comando polilinha: PL"
    Send-TextAndEnter -Text "PL" -AfterMs 350
    foreach ($p in $points) {
        Send-TextAndEnter -Text $p -AfterMs ([int]$cfg.Timing.BetweenPointMs)
    }
    Send-Keys -Keys "{ESC}" -DelayMs 500
    Write-Log "Polilinha finalizada com ESC."

    foreach ($command in $cfg.PostCommands) {
        $cmd = [string]$command
        Write-Log "Comando final: $cmd"
        Send-TextAndEnter -Text $cmd -AfterMs ([int]$cfg.Timing.AfterCommandMs)
    }

    Write-Log "Fluxo concluído."
    exit 0
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}
