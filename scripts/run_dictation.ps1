param(
    [ValidateSet("whispercpp", "python")]
    [string]$Backend = "whispercpp",
    [string]$KeyCombination = "ctrl_l+alt_l",
    [string]$ModelName = "medium",
    [string]$WhisperCppCli = $env:WHISPER_CLI_BIN,
    [string]$WhisperCppModel = $env:WHISPER_CLI_MODEL,
    [string]$WhisperCppArgs = "-otxt -l auto -oved GPU",
    [string]$FallbackBackend = "python",
    [switch]$NoFallback,
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"

$defaultCli = Join-Path $env:LOCALAPPDATA "whispercpp\openvino\bin\whisper-cli.exe"
$defaultModel = Join-Path $env:LOCALAPPDATA "whispercpp\models\ggml-large-v3.bin"

if (-not $WhisperCppCli -or -not (Test-Path $WhisperCppCli)) {
    if (Test-Path $defaultCli) {
        $WhisperCppCli = $defaultCli
    }
}

if (-not $WhisperCppModel -or -not (Test-Path $WhisperCppModel)) {
    if (Test-Path $defaultModel) {
        $WhisperCppModel = $defaultModel
    }
}

$pythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Missing $pythonExe"
}

$cmd = @(
    $pythonExe,
    ".\whisper-dictation.py",
    "--backend", $Backend,
    "-k", $KeyCombination
)

if ($Backend -eq "python") {
    $cmd += @("-m", $ModelName)
}

if ($Backend -eq "whispercpp") {
    if (-not $WhisperCppCli -or -not (Test-Path $WhisperCppCli)) {
        throw "whisper-cli path is invalid. Set WHISPER_CLI_BIN or pass -WhisperCppCli."
    }
    if (-not $WhisperCppModel -or -not (Test-Path $WhisperCppModel)) {
        throw "whisper model path is invalid. Set WHISPER_CLI_MODEL or pass -WhisperCppModel."
    }

    $cmd += @(
        "--whispercpp-cli", $WhisperCppCli,
        "--whispercpp-model", $WhisperCppModel,
        "--whispercpp-args", $WhisperCppArgs
    )

    if ($NoFallback) {
        $cmd += @("--disable-backend-fallback")
    } else {
        $cmd += @("--fallback-backend", $FallbackBackend)
    }
}

Write-Host "Command:"
Write-Host ($cmd -join " ")

if ($PrintOnly) {
    return
}

& $cmd[0] $cmd[1..($cmd.Length - 1)]
