# Anki Question Extractor - Tampermonkey Userscript

A Tampermonkey userscript that extracts medical questions and answers from ACEP PeerPrep and MKSAP 19 for import into Anki flashcards.

## Features

- 🎴 Floating extraction button on supported pages
- 🔍 Debug mode that outputs full page HTML to browser console
- 📋 Automatic clipboard copy of page HTML
- 🎨 Visual feedback (processing, success, error states)
- 🔧 Prepared for AnkiConnect integration

## Current Status: Debug Mode

This initial version focuses on **debugging and DOM inspection**. It will:
- Display a button in the bottom-right corner of ACEP and MKSAP pages
- Extract the full HTML of the page when clicked
- Output the HTML to the browser console (Developer Tools)
- Copy the HTML to your clipboard
- Attempt to locate elements using placeholder selectors (for future configuration)

## Installation

### Prerequisites
1. **Browser Extension**: Install [Tampermonkey](https://www.tampermonkey.net/) for your browser:
   - Chrome/Edge: [Tampermonkey on Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - Firefox: [Tampermonkey on Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)

### Installing the Script
1. Open Tampermonkey in your browser
2. Click on the Tampermonkey icon → **Dashboard**
3. Click the **"+"** tab (Create a new script)
4. Delete all the default code
5. Copy the entire contents of `question_extractor.user.js`
6. Paste it into the editor
7. Click **File** → **Save** (or press `Ctrl+S`)

## Usage

### Debug Mode with Local Server (Current Version)

#### Step 1: Start the Local Server

Open a terminal in the DougHub directory and run:

```powershell
.\scripts\start_extraction_server.ps1
```

Or manually:

```powershell
& "P:/Python Projects/DougHub/.venv/Scripts/python.exe" scripts/extraction_server.py
```

The server will start on `http://localhost:5000` and display:
```
🚀 TAMPERMONKEY EXTRACTION SERVER
Server is running on http://localhost:5000
Waiting for extractions from Tampermonkey script...
```

#### Step 2: Use the Userscript

1. **Navigate** to a question page on:
   - `https://www.acep.org/peerprep/*`
   - `https://learn.acep.org/*`
   - `https://mksap.acponline.org/mksap19/*`

2. **Look for the button**: A purple button labeled "🎴 Debug Extract" will appear in the bottom-right corner

3. **Open Developer Tools** (optional but recommended):
   - Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - Switch to the **Console** tab

4. **Click the button**: The button will change to "⏳ Extracting..." then "✓ Check Console!"

5. **Check the terminal**: The extracted data will appear in the terminal where the server is running:
   ```
   ================================================================================
   📥 NEW EXTRACTION RECEIVED at 2025-11-16T...
   ================================================================================
   🌐 URL: https://learn.acep.org/...
   🏥 Site: ACEP PeerPrep
   📊 Elements found: 542
   📏 HTML size: 245.3 KB
   ================================================================================
   
   📄 Body Text Preview:
   Question 1 of 10 A 45-year-old male presents with chest pain...
   
   🔍 Sample Elements (first 10):
     1. [div] div.question-text: Question 1 of 10 A 45-year-old male...
     2. [button] button.answer-choice: A. Administer aspirin
   ```

6. **Inspect browser console**: You'll also see detailed logs and a table of all extracted elements

### Finding the Right Selectors

To configure the script to extract actual questions:

1. **Run the debug script** on a question page
2. **Examine the HTML output** in the console
3. **Use browser DevTools** to inspect the question elements:
   - Right-click on the question text → "Inspect"
   - Note the element's class names, IDs, or structure
4. **Update the selectors** in the script:
   - Open the Tampermonkey editor
   - Find the `siteConfigs` object
   - Replace the `REPLACE_WITH_*` placeholders with actual CSS selectors

#### Example Selector Updates
```javascript
const siteConfigs = {
    "www.acep.org": {
        siteName: "ACEP PeerPrep",
        questionSelector: ".question-text",  // Replace with actual selector
        choicesSelector: ".answer-choice",   // Replace with actual selector
        explanationSelector: ".explanation", // Replace with actual selector
        correctAnswerSelector: ".correct"    // Replace with actual selector
    },
    // ... same for MKSAP
};
```

## Troubleshooting

### Button doesn't appear
- Verify you're on a URL that matches `@match` patterns in the script
- Check the Tampermonkey icon - ensure the script is enabled
- Open DevTools Console and look for `[Anki Extractor] Script loaded successfully`

### No HTML output in console
- Make sure Developer Tools Console is open before clicking
- Check for JavaScript errors in the console (red text)
- Verify the script is actually running (check Tampermonkey icon badge)

### Clipboard copy fails
- Some browsers restrict clipboard access
- You can still access the HTML from the console output
- Try copying directly from the console log

## Future Implementation

Once selectors are configured, the script will:
1. Extract structured Q&A data from the page
2. Send data to Anki via AnkiConnect
3. Provide immediate feedback on card creation
4. Fall back to clipboard copy if AnkiConnect unavailable

### AnkiConnect Setup (Future)
You will need to:
1. Install the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on in Anki
2. Configure CORS in Anki (Tools → Add-ons → AnkiConnect → Config):
   ```json
   {
       "webCorsOriginList": [
           "https://www.acep.org",
           "https://mksap.acponline.org"
       ]
   }
   ```
3. Have Anki running when extracting questions

## Development

### Project Structure
```
tampermonkey/
├── question_extractor.user.js   # The userscript
└── README.md                     # This file
```

### Key Functions
- `addExtractionUI()`: Injects the extraction button
- `handleExtraction()`: Main click handler (debug mode)
- `tryFindElement()`: Helper to test selectors
- `extractQnA()`: Future - extracts structured data
- `sendToAnki()`: Future - sends to AnkiConnect

### Modifying the Script
1. Open Tampermonkey Dashboard
2. Click on the script name
3. Make your changes
4. Save (`Ctrl+S`)
5. Refresh the target webpage

## License

Part of the DougHub project. See repository for license information.

## Support

For issues or questions, please open an issue in the DougHub repository.
