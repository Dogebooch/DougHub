# Demo script to test DougHub CLI functionality with Anki
# Run this script: .\scripts\demo_cli.ps1

Write-Host "`n=== DougHub CLI Demo ===" -ForegroundColor Cyan
Write-Host "This script demonstrates the CLI's ability to interact with Anki.`n" -ForegroundColor Gray

# 1. Check connection
Write-Host "[1/7] Checking AnkiConnect connection..." -ForegroundColor Yellow
doughub check-connection
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nAnki is not running. Starting Anki..." -ForegroundColor Red
    doughub launch-anki
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to start Anki. Please start it manually." -ForegroundColor Red
        exit 1
    }
}

# 2. List decks
Write-Host "`n[2/7] Listing all decks:" -ForegroundColor Yellow
doughub list-decks

# 3. List note types
Write-Host "`n[3/7] Listing all note types:" -ForegroundColor Yellow
doughub list-models

# 4. Show fields for Basic model
Write-Host "`n[4/7] Showing fields for 'Basic' note type:" -ForegroundColor Yellow
doughub show-model-fields --model "Basic"

# 5. List notes in Default deck (limited to 3)
Write-Host "`n[5/7] Showing first 3 notes from 'Default' deck:" -ForegroundColor Yellow
doughub list-notes --deck "Default" --limit 3

# 6. Create a test note
Write-Host "`n[6/7] Creating a test note..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$output = doughub add-note --deck "Default" --model "Basic" `
    --field "Front=DougHub CLI Test - $timestamp" `
    --field "Back=This note was created via the DougHub CLI to demonstrate functionality." `
    --tag "doughub-test" `
    --tag "automated" 2>&1

Write-Host $output

# Extract note ID from output
if ($output -match "Successfully created note with ID: (\d+)") {
    $noteId = $Matches[1]
    Write-Host "Created note ID: $noteId" -ForegroundColor Green
    
    # 7. Show the created note
    Write-Host "`n[7/7] Showing details of the newly created note:" -ForegroundColor Yellow
    doughub show-note --id $noteId
    
    Write-Host "`n=== Demo Complete! ===" -ForegroundColor Green
    Write-Host "Successfully demonstrated:" -ForegroundColor Gray
    Write-Host "  ✓ Connection verification" -ForegroundColor Green
    Write-Host "  ✓ Listing decks and models" -ForegroundColor Green
    Write-Host "  ✓ Inspecting model fields" -ForegroundColor Green
    Write-Host "  ✓ Querying existing notes" -ForegroundColor Green
    Write-Host "  ✓ Creating new notes" -ForegroundColor Green
    Write-Host "  ✓ Reading note details" -ForegroundColor Green
    Write-Host "`nNote ID $noteId can be reviewed in Anki." -ForegroundColor Cyan
} else {
    Write-Host "`nFailed to create test note." -ForegroundColor Red
    exit 1
}
