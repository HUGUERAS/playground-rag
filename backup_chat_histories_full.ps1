$ErrorActionPreference = 'SilentlyContinue'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$dest = "D:\CHAT_HISTORICOS_COMPLETO_$ts"
New-Item -Path $dest -ItemType Directory -Force | Out-Null

$copyList = @(
  @{ src = 'C:\Users\User\.continue\sessions'; dst = 'continue_sessions' },
  @{ src = 'C:\Users\User\.continue\dev_data'; dst = 'continue_dev_data' },
  @{ src = 'C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat'; dst = 'copilot_global' },
  @{ src = 'C:\Users\User\AppData\Roaming\Code\User\globalStorage\continue.continue'; dst = 'continue_global' },
  @{ src = 'C:\Users\User\AppData\Roaming\Code\User\globalStorage\emptyWindowChatSessions'; dst = 'vscode_emptyWindowChatSessions' },
  @{ src = 'C:\Users\User\.cursor'; dst = 'cursor' },
  @{ src = 'C:\Users\User\.codex'; dst = 'codex' },
  @{ src = 'C:\Users\User\.gemini\antigravity'; dst = 'antigravity' },
  @{ src = 'C:\Users\User\.claude'; dst = 'claude_home' },
  @{ src = 'C:\Users\User\AppData\Roaming\Claude'; dst = 'claude_roaming' },
  @{ src = 'C:\Users\User\AppData\Local\Claude'; dst = 'claude_local' },
  @{ src = 'C:\Users\User\AppData\Roaming\Cursor\User\workspaceStorage'; dst = 'cursor_workspaceStorage' },
  @{ src = 'C:\Users\User\AppData\Roaming\Cursor\User\globalStorage'; dst = 'cursor_globalStorage' }
)

foreach ($item in $copyList) {
  if (Test-Path $item.src) {
    $target = Join-Path $dest $item.dst
    Copy-Item -Path $item.src -Destination $target -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output ("COPIED=" + $item.src)
  } else {
    Write-Output ("MISSING=" + $item.src)
  }
}

$ws = 'C:\Users\User\AppData\Roaming\Code\User\workspaceStorage'
$wsDst = Join-Path $dest 'vscode_workspace_chat_resources'
New-Item -Path $wsDst -ItemType Directory -Force | Out-Null
if (Test-Path $ws) {
  Get-ChildItem -Path $ws -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $chatRes = Join-Path $_.FullName 'GitHub.copilot-chat\chat-session-resources'
    if (Test-Path $chatRes) {
      Copy-Item -Path $chatRes -Destination (Join-Path $wsDst $_.Name) -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Write-Output 'COPIED=VSCode workspace chat-session-resources'
}

$cursorWs = 'C:\Users\User\AppData\Roaming\Cursor\User\workspaceStorage'
$cursorWsDst = Join-Path $dest 'cursor_workspace_chat_resources'
New-Item -Path $cursorWsDst -ItemType Directory -Force | Out-Null
if (Test-Path $cursorWs) {
  Get-ChildItem -Path $cursorWs -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $possible1 = Join-Path $_.FullName 'chat-session-resources'
    $possible2 = Join-Path $_.FullName 'github.copilot-chat\chat-session-resources'
    if (Test-Path $possible1) {
      Copy-Item -Path $possible1 -Destination (Join-Path $cursorWsDst ($_.Name + '_chat')) -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $possible2) {
      Copy-Item -Path $possible2 -Destination (Join-Path $cursorWsDst ($_.Name + '_copilot_chat')) -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
  Write-Output 'COPIED=Cursor workspace chat resources'
}

$files = (Get-ChildItem -Path $dest -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$size = (Get-ChildItem -Path $dest -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
Write-Output ("DEST=" + $dest)
Write-Output ("FILES=" + $files)
Write-Output ("SIZE_GB=" + [math]::Round($size / 1GB, 3))
