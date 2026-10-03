param(
    [string]$Model = "rf",
    [string]$OutputDir = "C:\Users\dhruv\Desktop\reprolens\runs\RUN-001"
)

# Start timing
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# Run the docker command
$dockerCmd = @(
    "docker", "run", "--rm",
    "-v", "C:\Users\dhruv\Desktop\reprolens\repo:/repo",
    "-w", "/repo",
    "--cpus=2", "--memory=4g", "--memory-swap=4g",
    "--network=none", "--pids-limit=256",
    "reprolens-demo", "bash", "-c", "python benchmark.py --model=$Model"
)

try {
    $process = Start-Process -FilePath "docker" -ArgumentList $dockerCmd -Wait -RedirectStandardOutput "$OutputDir\stdout.log" -RedirectStandardError "$OutputDir\stderr.log" -PassThru
    $exitCode = $process.ExitCode
} catch {
    $exitCode = 1
    $_.Exception.Message | Out-File "$OutputDir\stderr.log" -Append
}

$stopwatch.Stop()
$wallSec = [math]::Round($stopwatch.Elapsed.TotalSeconds, 3)

# Save exit code
$exitCode | Out-File "$OutputDir\exit_code.txt"

# Save wall time
$wallSec | Out-File "$OutputDir\wall_sec.txt"

# Peak memory is not easily accessible in Windows Docker, use placeholder
"0" | Out-File "$OutputDir\peak_mb.txt"

Write-Host "Exit code: $exitCode"
Write-Host "Wall time: $wallSec seconds"