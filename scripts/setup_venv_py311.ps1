param(
    [string]$VenvPath = ".venv",
    [string]$Requirements = "requirements.txt",
    [string]$LockFile = "requirements-lock.txt",
    [string]$PythonCmd = ""
)

function Find-Python311 {
    $candidates = @(
        "py -3.11",
        "python3.11",
        "python3.11.exe",
        "C:\\Program Files\\Python311\\python.exe",
        "C:\\Python311\\python.exe"
    )
    foreach ($c in $candidates) {
        try {
            $out = & $c -V 2>&1
            if ($out -match "3\.11") { return $c }
        } catch { }
    }
    return $null
}

$pythonExe = ""
$pythonArgs = @()
if ($PythonCmd -ne "") {
    # Support passing a command with args like: 'py -3.11'
    $parts = $PythonCmd -split '\s+'
    $pythonExe = $parts[0]
    if ($parts.Length -gt 1) { $pythonArgs = $parts[1..($parts.Length - 1)] }
    try {
        $out = & $pythonExe @pythonArgs -V 2>&1
        if ($out -match "3\.11") {
            # good
        } else {
            Write-Error "Provided PythonCmd '$PythonCmd' is not Python 3.11 (version: $out)."
            exit 1
        }
    } catch {
        Write-Error "Cannot run provided PythonCmd '$PythonCmd'. Ensure the path is correct and executable."
        exit 1
    }
} else {
    $found = Find-Python311
    if (-not $found) {
        Write-Error "Python 3.11 not found. Install Python 3.11 or make it available as 'py -3.11' / 'python3.11'."
        exit 1
    }
    # If found, the finder returns a command string; split it into exe+args if needed
    $parts = $found -split '\s+'
    $pythonExe = $parts[0]
    if ($parts.Length -gt 1) { $pythonArgs = $parts[1..($parts.Length - 1)] }
}

Write-Host "Using Python command: $pythonExe $([string]::Join(' ', $pythonArgs))"

# Create venv
Write-Host "Creating venv at $VenvPath ..."
$createArgs = @()
if ($pythonArgs) { $createArgs += $pythonArgs }
$createArgs += @('-m','venv',$VenvPath)
& $pythonExe @createArgs

# Activate venv for the remainder of the script
$activate = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Error "Activation script not found at $activate"
    exit 1
}
. $activate

# Upgrade packaging tools
Write-Host "Upgrading pip/setuptools/wheel ..."
python -m pip install --upgrade pip setuptools wheel

# Install all requirements
if (-not (Test-Path $Requirements)) {
    Write-Error "Requirements file '$Requirements' not found."
    exit 1
}

Write-Host "Installing from $Requirements (this may take a while)..."
python -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed. See output above."
    exit $LASTEXITCODE
}

# Freeze to lockfile
Write-Host "Generating lockfile $LockFile ..."
python -m pip freeze | Out-File -Encoding UTF8 $LockFile

# Smoke test imports and print versions
Write-Host "Running smoke tests (numpy, torch, transformers, numba, librosa) ..."
$py = @'
import sys, importlib
names = ["numpy","torch","transformers","numba","librosa"]
out = []
for n in names:
    try:
        m = importlib.import_module(n)
        v = getattr(m, "__version__", "unknown")
        out.append(f"{n}={v}")
    except Exception as e:
        print(f"IMPORT-ERROR {n}: {e}", file=sys.stderr)
        sys.exit(2)
print("OK " + " ".join(out))
'@

# Write smoke test to a temporary file and run it to avoid shell quoting issues
$tmp = Join-Path $env:TEMP "indextts_smoke_test.py"
$py | Out-File -FilePath $tmp -Encoding UTF8
& python $tmp
$exit = $LASTEXITCODE
Remove-Item $tmp -ErrorAction SilentlyContinue
if ($exit -ne 0) {
    Write-Error "Smoke test failed."
    exit $exit
}
if ($LASTEXITCODE -ne 0) {
    Write-Error "Smoke test failed."
    exit $LASTEXITCODE
}

Write-Host "Setup complete. Activate the venv with: .\$VenvPath\Scripts\Activate.ps1"
exit 0
