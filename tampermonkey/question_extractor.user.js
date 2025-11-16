// ==UserScript==
// @name         Anki Question Extractor (MKSAP/ACEP) - Debug Mode
// @namespace    http://tampermonkey.net/
// @version      0.2.0
// @description  Extracts medical questions from MKSAP and ACEP for import into Anki (with debug mode)
// @author       DougHub
// @match        https://www.acep.org/*
// @match        https://*.acep.org/*
// @match        https://mksap.acponline.org/*
// @match        https://*.acponline.org/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=ankiweb.net
// @connect      localhost
// @connect      127.0.0.1
// @grant        GM_xmlhttpRequest
// @grant        GM_setClipboard
// @grant        GM_addStyle
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // --- Configuration ---
    const LOCAL_SERVER_URL = 'http://localhost:5000/extract';
    
    const siteConfigs = {
        "www.acep.org": {
            siteName: "ACEP PeerPrep",
            questionSelector: "REPLACE_WITH_ACEP_QUESTION_SELECTOR",
            choicesSelector: "REPLACE_WITH_ACEP_CHOICES_SELECTOR",
            explanationSelector: "REPLACE_WITH_ACEP_EXPLANATION_SELECTOR",
            correctAnswerSelector: "REPLACE_WITH_ACEP_CORRECT_ANSWER_SELECTOR"
        },
        "learn.acep.org": {
            siteName: "ACEP PeerPrep",
            questionSelector: "REPLACE_WITH_ACEP_QUESTION_SELECTOR",
            choicesSelector: "REPLACE_WITH_ACEP_CHOICES_SELECTOR",
            explanationSelector: "REPLACE_WITH_ACEP_EXPLANATION_SELECTOR",
            correctAnswerSelector: "REPLACE_WITH_ACEP_CORRECT_ANSWER_SELECTOR"
        },
        "mksap.acponline.org": {
            siteName: "MKSAP 19",
            questionSelector: "REPLACE_WITH_MKSAP_QUESTION_SELECTOR",
            choicesSelector: "REPLACE_WITH_MKSAP_CHOICES_SELECTOR",
            explanationSelector: "REPLACE_WITH_MKSAP_EXPLANATION_SELECTOR",
            correctAnswerSelector: "REPLACE_WITH_MKSAP_CORRECT_ANSWER_SELECTOR"
        }
    };

    // --- Styling ---
    GM_addStyle(`
        #anki-extractor-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        #anki-extractor-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }

        #anki-extractor-btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        #anki-extractor-btn.success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        }

        #anki-extractor-btn.error {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }

        #anki-extractor-btn.processing {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            cursor: wait;
        }

        .anki-extractor-icon {
            margin-right: 6px;
        }
    `);

    // --- Core Functions ---

    /**
     * Adds the extraction button to the page
     */
    function addExtractionUI() {
        const button = document.createElement('button');
        button.id = 'anki-extractor-btn';
        button.innerHTML = '<span class="anki-extractor-icon">🎴</span>Debug Extract';
        button.addEventListener('click', handleExtraction);
        document.body.appendChild(button);
        console.log('[Anki Extractor] UI button added successfully');
    }

    /**
     * Main extraction handler
     */
    async function handleExtraction() {
        const button = document.getElementById('anki-extractor-btn');
        
        try {
            // Update UI to processing state
            button.className = 'processing';
            button.innerHTML = '<span class="anki-extractor-icon">⏳</span>Extracting...';

            // Get the current site configuration
            const hostname = window.location.hostname;
            const config = siteConfigs[hostname];

            if (!config) {
                throw new Error(`No configuration found for site: ${hostname}`);
            }

            console.log('[Anki Extractor] Starting extraction for:', config.siteName);
            console.log('[Anki Extractor] Current URL:', window.location.href);
            console.log('[Anki Extractor] Config:', config);

            // Extract the full page HTML
            const pageHTML = document.documentElement.outerHTML;
            const bodyText = document.body.innerText;
            
            // Extract all elements with IDs, classes, and tags
            const allElements = document.querySelectorAll('*');
            const elementData = [];
            
            allElements.forEach((el, index) => {
                const tagName = el.tagName.toLowerCase();
                const id = el.id;
                const classes = Array.from(el.classList).join('.');
                const textContent = el.textContent ? el.textContent.trim().substring(0, 100) : '';
                
                // Only log elements that have IDs, classes, or meaningful text
                if (id || classes || (textContent && el.children.length === 0)) {
                    elementData.push({
                        index,
                        tag: tagName,
                        id: id || null,
                        classes: classes || null,
                        selector: id ? '#' + id : (classes ? tagName + '.' + classes : tagName),
                        text: textContent.replace(/\s+/g, ' ')
                    });
                }
            });
            
            // Prepare payload for local server
            const payload = {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                hostname: hostname,
                siteName: config.siteName,
                pageHTML: pageHTML,
                bodyText: bodyText,
                elementCount: elementData.length,
                elements: elementData
            };
            
            // Log to console
            console.log('═══════════════════════════════════════════════════════════');
            console.log('[Anki Extractor] ALL PAGE ELEMENTS:');
            console.log('═══════════════════════════════════════════════════════════');
            console.table(elementData);
            console.log('[Anki Extractor] Total elements found:', elementData.length);
            console.log('[Anki Extractor] Payload size:', Math.round(JSON.stringify(payload).length / 1024), 'KB');
            console.log('═══════════════════════════════════════════════════════════');

            // Send to local server
            await sendToLocalServer(payload);

            // Copy HTML to clipboard for convenience
            try {
                GM_setClipboard(pageHTML);
                console.log('[Anki Extractor] ✓ HTML copied to clipboard');
            } catch (clipboardErr) {
                console.warn('[Anki Extractor] Could not copy to clipboard:', clipboardErr);
            }

            // Success state
            button.className = 'success';
            button.innerHTML = '<span class="anki-extractor-icon">✓</span>Check Console!';

            // Reset button after delay
            setTimeout(() => {
                button.className = '';
                button.innerHTML = '<span class="anki-extractor-icon">🎴</span>Debug Extract';
            }, 3000);

        } catch (error) {
            console.error('[Anki Extractor] Error during extraction:', error);
            
            // Error state
            button.className = 'error';
            button.innerHTML = '<span class="anki-extractor-icon">✗</span>Error!';

            // Reset button after delay
            setTimeout(() => {
                button.className = '';
                button.innerHTML = '<span class="anki-extractor-icon">🎴</span>Debug Extract';
            }, 3000);
        }
    }

    /**
     * Helper function to try finding an element and log results
     */
    function tryFindElement(label, selector) {
        if (selector.includes('REPLACE_WITH')) {
            console.log(`[Anki Extractor] ${label}: Selector not configured yet (${selector})`);
            return null;
        }

        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            console.log(`[Anki Extractor] ${label}: Found ${elements.length} element(s) with selector "${selector}"`);
            console.log(`[Anki Extractor] ${label} content:`, elements[0].textContent.trim().substring(0, 200) + '...');
            return elements[0];
        } else {
            console.warn(`[Anki Extractor] ${label}: No elements found with selector "${selector}"`);
            return null;
        }
    }

    /**
     * Extract Q&A data from the page (for future use)
     */
    function extractQnA() {
        const hostname = window.location.hostname;
        const config = siteConfigs[hostname];

        if (!config) {
            throw new Error(`No configuration found for site: ${hostname}`);
        }

        // This will be implemented once we have the correct selectors
        const data = {
            site: config.siteName,
            url: window.location.href,
            question: null,
            choices: [],
            explanation: null,
            correctAnswer: null
        };

        return data;
    }

    /**
     * Send extracted data to local server
     */
    function sendToLocalServer(payload) {
        return new Promise((resolve, reject) => {
            console.log('[Anki Extractor] Sending data to local server:', LOCAL_SERVER_URL);
            
            GM_xmlhttpRequest({
                method: 'POST',
                url: LOCAL_SERVER_URL,
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify(payload),
                onload: function(response) {
                    if (response.status === 200) {
                        console.log('[Anki Extractor] ✓ Data sent to server successfully');
                        console.log('[Anki Extractor] Server response:', response.responseText);
                        resolve(response);
                    } else {
                        console.warn('[Anki Extractor] Server returned status:', response.status);
                        console.warn('[Anki Extractor] Response:', response.responseText);
                        reject(new Error('Server returned status: ' + response.status));
                    }
                },
                onerror: function(error) {
                    console.error('[Anki Extractor] ✗ Failed to send data to server');
                    console.error('[Anki Extractor] Error:', error);
                    console.warn('[Anki Extractor] Make sure the local server is running on', LOCAL_SERVER_URL);
                    reject(error);
                },
                ontimeout: function() {
                    console.error('[Anki Extractor] ✗ Request timed out');
                    reject(new Error('Request timed out'));
                }
            });
        });
    }
    
    /**
     * Send extracted data to Anki via AnkiConnect (placeholder for future)
     */
    function sendToAnki(qnaData) {
        console.log('[Anki Extractor] sendToAnki called (not implemented yet):', qnaData);
        
        // Future implementation will use GM_xmlhttpRequest to post to localhost:8765
        // const payload = {
        //     action: "addNote",
        //     version: 6,
        //     params: {
        //         note: {
        //             deckName: "Medicine",
        //             modelName: "Basic-Q&A-with-Context",
        //             fields: {
        //                 Question: qnaData.question,
        //                 Answer: qnaData.correctAnswer,
        //                 Explanation: qnaData.explanation,
        //                 Source: qnaData.site
        //             },
        //             tags: ["extracted"]
        //         }
        //     }
        // };
    }

    // --- Initialize ---
    
    /**
     * Wait for page to be fully loaded before adding UI
     */
    function init() {
        console.log('[Anki Extractor] Script loaded successfully');
        console.log('[Anki Extractor] Current URL:', window.location.href);
        console.log('[Anki Extractor] Hostname:', window.location.hostname);
        console.log('[Anki Extractor] Document ready state:', document.readyState);
        
        // Try multiple approaches to ensure button is added
        if (document.body) {
            console.log('[Anki Extractor] document.body exists, adding button immediately');
            addExtractionUI();
        } else {
            console.log('[Anki Extractor] document.body not ready, waiting for DOMContentLoaded');
            document.addEventListener('DOMContentLoaded', () => {
                console.log('[Anki Extractor] DOMContentLoaded fired, adding button');
                addExtractionUI();
            });
        }
        
        // Backup: try again after a short delay
        setTimeout(() => {
            const existingButton = document.getElementById('anki-extractor-btn');
            if (!existingButton && document.body) {
                console.log('[Anki Extractor] Button not found after delay, adding now');
                addExtractionUI();
            } else if (existingButton) {
                console.log('[Anki Extractor] Button already exists');
            } else {
                console.warn('[Anki Extractor] document.body still not available!');
            }
        }, 1000);
    }

    // Start the script
    init();

})();
