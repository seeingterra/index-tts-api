# Start the FastAPI app inside a .venv
# Usage: .\start_api.ps1

$venvPath = "$PSScriptRoot\..\.venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath"
    python -m venv $venvPath
}

# Activate
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
. $activate

# Ensure pip is up-to-date and install requirements if not already installed
python -m pip install --upgrade pip
if (Test-Path "$PSScriptRoot\..\requirements.txt") {
    python -m pip install -r "$PSScriptRoot\..\requirements.txt"
}

# Run the FastAPI server (adjust host/port as needed)
Write-Host "Starting FastAPI app..."
python -m uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000
