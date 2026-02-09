param(
    [string]$RepoDir = "temp/third_party/whisper.cpp",
    [string]$ModelName = "base"
)

$ErrorActionPreference = "Stop"
$isEnglishOnlyModel = $ModelName -match "\.en$"
$smokeLanguage = if ($isEnglishOnlyModel) { "en" } else { "auto" }

if ($isEnglishOnlyModel) {
    Write-Warning "Using English-only model '$ModelName'. This is not suitable for Polish dictation quality benchmarks."
}

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command '$Name'. $Hint"
    }
}

function Ensure-WingetPackage([string]$Id, [string]$InstallArgs = "") {
    $found = winget list --id $Id --accept-source-agreements 2>$null
    if ($LASTEXITCODE -eq 0 -and $found) {
        Write-Host "[ok] $Id already installed"
        return
    }

    $base = "winget install --id $Id --silent --accept-package-agreements --accept-source-agreements"
    if ($InstallArgs) {
        Invoke-Expression "$base --override `"$InstallArgs`""
    } else {
        Invoke-Expression $base
    }
}

function Get-OpenVinoCmakeDir([string]$VenvPython) {
    & $VenvPython -c "import openvino, pathlib; print((pathlib.Path(openvino.__file__).resolve().parent / 'cmake').as_posix())"
}

function Run-CmdScript([string]$Body) {
    $cmdPath = Join-Path $env:TEMP "whisper_openvino_setup.cmd"
    Set-Content -Path $cmdPath -Value $Body -Encoding ascii
    cmd /c $cmdPath
    if ($LASTEXITCODE -ne 0) {
        throw "Command script failed: $cmdPath"
    }
}

Write-Host "== Whisper OpenVINO Windows Setup =="

Require-Command winget "Install App Installer from Microsoft Store."
Require-Command git "Install Git first."
Require-Command py "Install Python launcher first."

Ensure-WingetPackage "Kitware.CMake"
Ensure-WingetPackage "Microsoft.VisualStudio.2022.BuildTools" "--wait --quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"

$venvPython = (Resolve-Path ".venv/Scripts/python.exe").Path
& $venvPython -m pip install openvino

$openvinoCmakeDir = Get-OpenVinoCmakeDir -VenvPython $venvPython

if (-not (Test-Path $RepoDir)) {
    New-Item -ItemType Directory -Path (Split-Path $RepoDir -Parent) -Force | Out-Null
    git clone https://github.com/ggml-org/whisper.cpp $RepoDir
} else {
    git -C $RepoDir pull --ff-only
}

$repoPath = (Resolve-Path $RepoDir).Path
$modelDir = Join-Path $repoPath "models"
$modelTarget = Join-Path $modelDir ("ggml-" + $ModelName + ".bin")

$modelFromEnv = [Environment]::GetEnvironmentVariable("WHISPER_CLI_MODEL", "User")
if ($modelFromEnv -and (Test-Path $modelFromEnv)) {
    Copy-Item -Path $modelFromEnv -Destination $modelTarget -Force
} elseif (-not (Test-Path $modelTarget)) {
    $url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$ModelName.bin"
    & curl.exe -L --fail --retry 3 --retry-delay 2 -o $modelTarget $url
}

$vsDev = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
if (-not (Test-Path $vsDev)) {
    throw "VsDevCmd not found at: $vsDev"
}

$cmakeExe = "C:\Program Files\CMake\bin\cmake.exe"
if (-not (Test-Path $cmakeExe)) {
    throw "cmake.exe not found at: $cmakeExe"
}

$buildScript = @"
@echo off
call "$vsDev" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b 1
set OpenVINO_DIR=$openvinoCmakeDir
cd /d "$repoPath"
"$cmakeExe" -B build-openvino -DWHISPER_OPENVINO=1 -DCMAKE_BUILD_TYPE=Release
"$cmakeExe" --build build-openvino --config Release -j
"@
Run-CmdScript $buildScript

$py310 = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe"
if (-not (Test-Path $py310)) {
    throw "Python 3.10 not found at: $py310"
}

Push-Location $modelDir
if (-not (Test-Path "openvino_conv_env\Scripts\python.exe")) {
    & $py310 -m venv openvino_conv_env
}
& .\openvino_conv_env\Scripts\python.exe -m pip install --upgrade pip
& .\openvino_conv_env\Scripts\python.exe -m pip install -r requirements-openvino.txt onnxscript
$env:PYTHONIOENCODING = "utf-8"
& .\openvino_conv_env\Scripts\python.exe .\convert-whisper-to-openvino.py --model $ModelName
Pop-Location

$localModelDir = Join-Path $env:LOCALAPPDATA "whispercpp\models"
New-Item -ItemType Directory -Path $localModelDir -Force | Out-Null
Copy-Item -Path (Join-Path $modelDir ("ggml-$ModelName.bin")) -Destination (Join-Path $localModelDir ("ggml-$ModelName.bin")) -Force
Copy-Item -Path (Join-Path $modelDir ("ggml-$ModelName-encoder-openvino.xml")) -Destination (Join-Path $localModelDir ("ggml-$ModelName-encoder-openvino.xml")) -Force
Copy-Item -Path (Join-Path $modelDir ("ggml-$ModelName-encoder-openvino.bin")) -Destination (Join-Path $localModelDir ("ggml-$ModelName-encoder-openvino.bin")) -Force

$builtCli = Join-Path $repoPath "build-openvino\bin\Release\whisper-cli.exe"
if (-not (Test-Path $builtCli)) {
    throw "Built whisper-cli.exe not found: $builtCli"
}

$openvinoLibs = (Resolve-Path ".venv/Lib/site-packages/openvino/libs").Path
$stableCliDir = Join-Path $env:LOCALAPPDATA "whispercpp\openvino\bin"
New-Item -ItemType Directory -Force -Path $stableCliDir | Out-Null
Copy-Item -Path (Join-Path (Split-Path $builtCli -Parent) "*") -Destination $stableCliDir -Force
Copy-Item -Path (Join-Path $openvinoLibs "*") -Destination $stableCliDir -Force

$newModel = Join-Path $localModelDir ("ggml-$ModelName.bin")
$newCli = Join-Path $stableCliDir "whisper-cli.exe"
setx WHISPER_CLI_BIN $newCli | Out-Null
setx WHISPER_CLI_MODEL $newModel | Out-Null
[Environment]::SetEnvironmentVariable("WHISPER_CLI_BIN", $newCli, "User")
[Environment]::SetEnvironmentVariable("WHISPER_CLI_MODEL", $newModel, "User")

Write-Host ""
Write-Host "Setup complete."
Write-Host "WHISPER_CLI_BIN=$newCli"
Write-Host "WHISPER_CLI_MODEL=$newModel"
Write-Host ""
Write-Host "Smoke test command:"
Write-Host "`"$newCli`" -m `"$newModel`" -f tests/audio/test_english_5s_20250630_094048.wav -l $smokeLanguage -otxt -of `"$env:TEMP\whisper_cli_openvino_smoke\sample`" -oved GPU"
