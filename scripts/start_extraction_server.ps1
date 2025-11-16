# Start the extraction server
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Tampermonkey Extraction Server" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This server will receive data from the Tampermonkey script" -ForegroundColor Yellow
Write-Host "and display it in this terminal for debugging.`n" -ForegroundColor Yellow

Write-Host "Instructions:" -ForegroundColor Green
Write-Host "1. Make sure this script is running" -ForegroundColor White
Write-Host "2. Update your Tampermonkey script with the latest version" -ForegroundColor White
Write-Host "3. Navigate to an ACEP or MKSAP question page" -ForegroundColor White
Write-Host "4. Click the 'Debug Extract' button" -ForegroundColor White
Write-Host "5. Watch the data appear here!`n" -ForegroundColor White

Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Gray

# Activate virtual environment and run the server
& "$PSScriptRoot/../.venv/Scripts/python.exe" "$PSScriptRoot/extraction_server.py"
