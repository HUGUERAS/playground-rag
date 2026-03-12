$ErrorActionPreference = 'SilentlyContinue'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$destinationRoot = "D:\PROGRAMACAO_COLETA_$timestamp"
$logFile = Join-Path $destinationRoot 'coleta.log'

New-Item -Path $destinationRoot -ItemType Directory -Force | Out-Null
"[START] $(Get-Date -Format s)" | Out-File -FilePath $logFile -Encoding utf8
"[DEST] $destinationRoot" | Out-File -FilePath $logFile -Append -Encoding utf8

$codeExtensions = @(
    '.py','.ipynb','.js','.jsx','.ts','.tsx','.mjs','.cjs',
    '.java','.kt','.kts','.scala','.groovy','.gradle',
    '.c','.h','.cpp','.hpp','.cc','.hh',
    '.cs','.vb','.fs',
    '.go','.rs','.swift','.dart',
    '.php','.rb','.pl','.lua','.r','.jl',
    '.sh','.bash','.zsh','.ps1','.psm1','.psd1','.bat','.cmd',
    '.sql','.graphql',
    '.html','.htm','.css','.scss','.sass','.less','.vue','.svelte',
    '.xml','.json','.jsonc','.yaml','.yml','.toml','.ini','.cfg','.conf',
    '.md','.rst',
    '.dxf','.dwg',
    '.kml','.kmz','.shp','.shx','.dbf','.prj','.cpg','.qmd'
)

$manualDocExtensions = @('.pdf','.doc','.docx','.odt','.rtf')
$manualNameRegex = [regex]'(?i)(manual|requeriment|requerimento|requirements?)'

$imageExtensions = @(
    '.jpg','.jpeg','.png','.gif','.bmp','.webp','.tif','.tiff','.ico','.svg',
    '.heic','.heif','.raw','.cr2','.nef','.arw'
)

$specialNames = @(
    'Dockerfile','docker-compose.yml','docker-compose.yaml','Makefile','CMakeLists.txt',
    'requirements.txt','pyproject.toml','Pipfile','Pipfile.lock','poetry.lock',
    'package.json','package-lock.json','yarn.lock','pnpm-lock.yaml',
    'go.mod','go.sum','Cargo.toml','Cargo.lock','Gemfile','Gemfile.lock',
    '.gitignore','.gitattributes','.editorconfig','.env.example'
)

$skipRegex = [regex]'\\(node_modules|\.git|dist|build|out|target|__pycache__|\.venv|venv|\.next|\.nuxt|\.cache|\.mypy_cache|\.pytest_cache|System Volume Information|\$Recycle\.Bin|Windows|Program Files|Program Files \(x86\)|ProgramData)\\'

$drives = Get-PSDrive -PSProvider FileSystem | Select-Object -ExpandProperty Root
$copied = 0
$failed = 0
$duplicateSkipped = 0
$seenHashes = New-Object 'System.Collections.Generic.HashSet[string]'

foreach ($drive in $drives) {
    "[DRIVE] $drive" | Out-File -FilePath $logFile -Append -Encoding utf8

    Get-ChildItem -LiteralPath $drive -Recurse -File -Force | ForEach-Object {
        $full = $_.FullName

        if ($full -like "$destinationRoot*") { return }
        if ($skipRegex.IsMatch($full)) { return }

        $ext = $_.Extension.ToLowerInvariant()
        if ($imageExtensions -contains $ext) { return }

        $isCodeExt = $codeExtensions -contains $ext
        $isSpecial = $specialNames -contains $_.Name
        $isManualDoc = ($manualDocExtensions -contains $ext) -and $manualNameRegex.IsMatch($_.Name)

        if (-not ($isCodeExt -or $isSpecial -or $isManualDoc)) { return }

        try {
            $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
            if (-not $seenHashes.Add($hash)) {
                $duplicateSkipped++
                return
            }
        } catch {
            $failed++
            "[ERROR_HASH] $full" | Out-File -FilePath $logFile -Append -Encoding utf8
            return
        }

        $driveLetter = $full.Substring(0,1)
        if ($full.Length -gt 3) {
            $subPath = $full.Substring(3)
        } else {
            $subPath = $_.Name
        }

        $target = Join-Path $destinationRoot (Join-Path $driveLetter $subPath)
        $targetDir = Split-Path -Path $target -Parent

        try {
            if (-not (Test-Path -LiteralPath $targetDir)) {
                New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
            }

            Copy-Item -LiteralPath $full -Destination $target -Force
            $copied++

            if (($copied % 500) -eq 0) {
                "[PROGRESS] copied=$copied dup_skipped=$duplicateSkipped failed=$failed last=$full" | Out-File -FilePath $logFile -Append -Encoding utf8
            }
        } catch {
            $failed++
            "[ERROR] $full" | Out-File -FilePath $logFile -Append -Encoding utf8
        }
    }
}

"[END] $(Get-Date -Format s) copied=$copied dup_skipped=$duplicateSkipped failed=$failed" | Out-File -FilePath $logFile -Append -Encoding utf8
Write-Output "DESTINATION=$destinationRoot"
Write-Output "COPIED=$copied"
Write-Output "DUPLICATES_SKIPPED=$duplicateSkipped"
Write-Output "FAILED=$failed"
Write-Output "LOG=$logFile"
