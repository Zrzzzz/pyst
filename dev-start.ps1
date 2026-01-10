# Development startup script for Windows PowerShell
# Start both Flask backend and Vue 3 frontend

Write-Host ""
Write-Host "=========================================="
Write-Host "Stock Monitor System - Development Start"
Write-Host "=========================================="
Write-Host ""

# Check if Python is installed
try {
    python --version | Out-Null
} catch {
    Write-Host "Error: Python not found. Please install Python 3.12+"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pnpm is installed
try {
    pnpm --version | Out-Null
} catch {
    Write-Host "Error: pnpm not found. Please install pnpm"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Environment check passed"
Write-Host ""

# Start backend
Write-Host "Starting Flask backend..."
Write-Host "Address: http://127.0.0.1:5000"
Start-Process python -ArgumentList "app.py" -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Vue 3 frontend..."
Write-Host "Address: http://127.0.0.1:3000"
Start-Process cmd -ArgumentList "/k cd frontend && pnpm dev" -WindowStyle Normal

Write-Host ""
Write-Host "=========================================="
Write-Host "Development services started"
Write-Host "=========================================="
Write-Host ""
Write-Host "Access: http://127.0.0.1:3000"
Write-Host ""
Write-Host "Close the windows or press Ctrl+C to stop services"
Write-Host ""

Read-Host "Press Enter to exit"

