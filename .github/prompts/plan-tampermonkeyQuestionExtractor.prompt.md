# Tampermonkey Question Extractor Plan

## 1. Overview

This plan outlines the creation of a Tampermonkey userscript to extract medical questions and answers from `acep.org` (PeerPrep) and `mksap.org` (MKSAP 19). The primary goal is to automate the transfer of educational content into Anki flashcards for efficient study.

-   **Goal**: Develop a userscript that can parse Q&A pages, extract the relevant text fields, and send them directly to a running Anki instance via the AnkiConnect addon.
-   **Non-Goal**: This plan does not cover the creation of the Anki Note Types or decks themselves. The user is expected to have a pre-existing Anki setup.

## 2. Context and Constraints

-   **Repository Location**: The userscript code will be a new addition to the `DougHub` repository. It will be self-contained and will not interact with the existing Python codebase. A new directory `tampermonkey/` will be created at the project root to house the script and its documentation.
-   **External Dependencies**:
    -   The script's functionality is critically dependent on the DOM structure of `acep.org` and `mksap.org`. Any site redesign will break the script and require maintenance.
    -   The end-user must have the Tampermonkey (or equivalent) browser extension installed.
    -   Direct Anki import requires the AnkiConnect addon to be installed in Anki, and Anki must be running during extraction.
-   **Security**: The script will make HTTP requests to `localhost`. The Tampermonkey `@connect` directive should be used to whitelist this domain, ensuring the script does not communicate with unauthorized external servers.

## 3. Implementation Checkpoints (for Claude + Copilot)

### Checkpoint 1: Project Scaffolding
1.  **Action**: Create a new directory: `tampermonkey/`.
2.  **Action**: Inside `tampermonkey/`, create a new file named `question_extractor.user.js`.
3.  **Action**: Populate `question_extractor.user.js` with the initial Tampermonkey header. Use Copilot to assist with generating the standard header format.

    ```javascript
    // ==UserScript==
    // @name         Anki Question Extractor (MKSAP/ACEP)
    // @namespace    http://tampermonkey.net/
    // @version      0.1
    // @description  Extracts medical questions from MKSAP and ACEP for import into Anki.
    // @author       Your Name
    // @match        https://www.acep.org/peerprep/*
    // @match        https://mksap.acponline.org/mksap19/*
    // @icon         https://www.google.com/s2/favicons?sz=64&domain=ankiweb.net
    // @connect      localhost
    // @grant        GM_xmlhttpRequest
    // @grant        GM_setClipboard
    // @grant        GM_addStyle
    // ==/UserScript==

    (function() {
        'use strict';

        // --- Script logic will go here ---
    })();
    ```

### Checkpoint 2: DOM Analysis & Selector Definition
-   **This is a manual analysis step for the developer.** Before proceeding, you must inspect the live question pages on both ACEP and MKSAP to find the correct CSS selectors.
-   **Action**: Create a configuration object at the top of the script to hold site-specific selectors. This modular design will make future maintenance easier.

    ```javascript
    const siteConfigs = {
        "www.acep.org": {
            questionSelector: "REPLACE_WITH_ACEP_QUESTION_SELECTOR",
            choicesSelector: "REPLACE_WITH_ACEP_CHOICES_SELECTOR",
            // ... add selectors for explanation, correct answer indicator, etc.
        },
        "mksap.acponline.org": {
            questionSelector: "REPLACE_WITH_MKSAP_QUESTION_SELECTOR",
            choicesSelector: "REPLACE_WITH_MKSAP_CHOICES_SELECTOR",
            // ... add selectors for explanation, correct answer indicator, etc.
        }
    };
    ```

### Checkpoint 3: UI and Core Extraction Logic
1.  **Action**: Implement a function `addExtractionUI()` that injects a floating "Extract to Anki" button onto the page. Use `GM_addStyle` to style it to be visible but not obstructive.
2.  **Action**: Implement the main extraction function, `extractQnA()`. This function should:
    -   Determine the current site from `window.location.hostname`.
    -   Use the corresponding selectors from `siteConfigs` to grab the text content for the question, answer choices, and explanation.
    -   Identify the correct answer. This may require observing class names or attributes on the selected choice.
    -   Return a structured JavaScript object containing all extracted data.

### Checkpoint 4: AnkiConnect Integration
1.  **Action**: Implement the `sendToAnki(qnaData)` function.
2.  **Details**: This function will use `GM_xmlhttpRequest` to make a POST request to `http://localhost:8765`. The request body must be a JSON object matching the AnkiConnect `addNote` action format.
    -   **Use Copilot** to help structure the `GM_xmlhttpRequest` call, including `method`, `url`, `data`, `headers`, `onload`, and `onerror`.
    -   The `data` payload should look like this (customize `deckName`, `modelName`, and `fields` to match your Anki setup):

    ```json
    {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Medicine",
                "modelName": "Basic-Q&A-with-Context",
                "fields": {
                    "Question": "...", // from qnaData
                    "Answer": "...",   // from qnaData
                    "Explanation": "...", // from qnaData
                    "Source": "..." // e.g., 'MKSAP 19'
                },
                "tags": ["mksap19"]
            }
        }
    }
    ```
3.  **Action**: Hook this function up to the UI button's click event. Provide visual feedback to the user on success or failure (e.g., changing button text/color).

## 4. Zen MCP Integration

-   **After Checkpoint 4**: Run `codereview` on `tampermonkey/question_extractor.user.js`. Ask it to check for:
    -   Robustness of DOM parsing (handling cases where selectors might not be found).
    -   Correctness of the `GM_xmlhttpRequest` implementation.
    -   General JavaScript best practices.
-   **Before Finalizing**: Run `docgen` on the `tampermonkey/` directory. Instruct it to create a `README.md` file that explains:
    -   What the script does.
    -   How to install it in Tampermonkey.
    -   The required AnkiConnect setup (including CORS configuration).
    -   The expected Anki Note Type structure.
-   **Pre-commit**: Use the `precommit` tool to perform a final lint and style check on the `.user.js` file.

## 5. Behavior Changes

-   This is a net-new feature. It introduces a userscript that runs in the user's browser but does not modify any of the existing `DougHub` application code or behavior.

## 6. End-User Experience

-   **UI**: A floating button with an Anki logo will appear on supported question pages.
-   **Feedback**:
    -   On click, the button should provide immediate feedback (e.g., "Extracting...").
    -   On success, it should confirm the card was added (e.g., "Success!").
    -   On failure, it must provide a helpful error message (e.g., "Error: Could not connect to Anki. Is it running?").
-   **Clipboard Fallback**: As a fallback, if the AnkiConnect call fails, the extracted data should be copied to the clipboard in a structured format (e.g., TSV), allowing for manual import. The user should be notified that the data has been copied.

## 7. Validation

Validation will be primarily manual due to the nature of the userscript.

1.  **Setup**: Install the script in Tampermonkey and ensure Anki with AnkiConnect is running.
2.  **Test Case 1 (MKSAP)**:
    -   Navigate to an MKSAP question page.
    -   Verify the "Extract to Anki" button is present.
    -   Click the button.
    -   Verify a new card is created in the target Anki deck with all fields correctly populated.
3.  **Test Case 2 (ACEP)**:
    -   Repeat the process for an ACEP PeerPrep question page.
4.  **Test Case 3 (Error Handling)**:
    -   Shut down Anki.
    -   Click the extract button.
    -   Verify that a clear error message is displayed and that the extracted content has been copied to the clipboard as a fallback.
5.  **Test Case 4 (DOM Failure)**:
    -   Temporarily change a selector in the script to be invalid.
    -   Reload the page and click the button.
    -   Verify a graceful failure message is shown (e.g., "Error: Could not find question text on page.").
