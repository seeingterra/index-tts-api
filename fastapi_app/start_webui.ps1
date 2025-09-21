# Start the Web UI script inside a .venv
# Usage: .\start_webui.ps1

$venvPath = "$PSScriptRoot\..\.venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath"
    python -m venv $venvPath
}

# Activate
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
. $activate

# Install requirements
python -m pip install --upgrade pip
if (Test-Path "$PSScriptRoot\..\requirements.txt") {
    python -m pip install -r "$PSScriptRoot\..\requirements.txt"
}

# Run the web UI (adjust filename if webui.py is moved)
Write-Host "Starting Web UI..."
python ..\webui.py
