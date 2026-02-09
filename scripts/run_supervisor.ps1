param(
    [ValidateSet("whispercpp", "python")]
    [string]$Backend = "whispercpp",
    [ValidateSet("tiny", "base", "small", "medium", "large")]
    [string]$PythonModel = "medium",
    [string]$CppModel = "large-v3",
    [string]$KeyCombination = "ctrl_l+alt_l",
    [string]$WhisperCppCli = $env:WHISPER_CLI_BIN,
    [switch]$NoTray
)

$ErrorActionPreference = "Stop"

$pythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Missing $pythonExe"
}

if (-not $WhisperCppCli) {
    $defaultCli = Join-Path $env:LOCALAPPDATA "whispercpp\openvino\bin\whisper-cli.exe"
    if (Test-Path $defaultCli) {
        $WhisperCppCli = $defaultCli
    }
}

$cmd = @(
    $pythonExe,
    ".\whisper-dictation-supervisor.py",
    "--backend", $Backend,
    "--python-model", $PythonModel,
    "--cpp-model", $CppModel,
    "--key-combination", $KeyCombination
)

if ($WhisperCppCli) {
    $cmd += @("--whispercpp-cli", $WhisperCppCli)
}

if ($NoTray) {
    $cmd += "--no-tray"
}

Write-Host "Command:"
Write-Host ($cmd -join " ")

& $cmd[0] $cmd[1..($cmd.Length - 1)]
