# Quick verification script for DougHub CLI
# Run this script: .\scripts\verify_cli.ps1

Write-Host "`n=== Quick Anki Connection Test ===" -ForegroundColor Cyan

# Check if Anki is running
Write-Host "`nChecking connection..." -ForegroundColor Yellow
doughub check-connection

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ AnkiConnect is accessible!" -ForegroundColor Green
    
    Write-Host "`nAvailable decks:" -ForegroundColor Yellow
    doughub list-decks
    
    Write-Host "`nAvailable note types:" -ForegroundColor Yellow
    doughub list-models
    
    Write-Host "`n=== Connection Test Passed! ===" -ForegroundColor Green
    Write-Host "Run 'doughub --help' to see all available commands." -ForegroundColor Gray
} else {
    Write-Host "`n✗ AnkiConnect is not accessible." -ForegroundColor Red
    Write-Host "Make sure Anki is running with the AnkiConnect add-on installed." -ForegroundColor Yellow
    Write-Host "`nTry running: doughub launch-anki" -ForegroundColor Cyan
    exit 1
}
