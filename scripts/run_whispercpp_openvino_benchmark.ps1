param(
    [int]$Runs = 3,
    [string]$AudioPattern = "test_*.wav",
    [string[]]$QualityFiles = @(
        "test_english*.wav",
        "test_polish_10s*.wav",
        "test_polish_5s*.wav"
    ),
    [string]$WhisperCli = $env:WHISPER_CLI_BIN,
    [string]$WhisperModel = $env:WHISPER_CLI_MODEL,
    [string]$Candidate = "whispercpp-openvino-gpu=-otxt -l auto -oved GPU"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Missing .venv\Scripts\python.exe"
}

if (-not $WhisperCli -or -not (Test-Path $WhisperCli)) {
    throw "whisper-cli not found. Set WHISPER_CLI_BIN or pass -WhisperCli."
}

if (-not $WhisperModel -or -not (Test-Path $WhisperModel)) {
    throw "whisper model not found. Set WHISPER_CLI_MODEL or pass -WhisperModel."
}

$cmd = @(
    ".\.venv\Scripts\python.exe",
    "scripts/windows_acceleration_benchmark.py",
    "--skip-python",
    "--runs", $Runs,
    "--audio-pattern", $AudioPattern,
    "--whispercpp-cli", $WhisperCli,
    "--whispercpp-model", $WhisperModel,
    "--whispercpp-candidate", $Candidate
)

foreach ($pattern in $QualityFiles) {
    $cmd += @("--quality-files", $pattern)
}

Write-Host "Running whisper.cpp benchmark (no build, no Python baseline)..."
Write-Host ("Command: " + ($cmd -join " "))
& $cmd[0] $cmd[1..($cmd.Length - 1)]
