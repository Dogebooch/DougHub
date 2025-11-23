"""UI styling constants for DougHub application.

This module defines color schemes, spacing, and typography constants
to ensure consistent styling across the application.
"""

# Color palette
PRIMARY_COLOR = "#4A90E2"  # Blue accent color
NEUTRAL_BG = "#F5F5F5"  # Light gray background
TEXT_PRIMARY = "#333333"  # Dark gray for primary text
TEXT_SECONDARY = "#666666"  # Medium gray for secondary text

# Spacing (in pixels)
SPACING_XS = 4
SPACING_S = 8
SPACING_M = 16
SPACING_L = 24

# Font sizes (in pixels)
FONT_SIZE_S = 12
FONT_SIZE_M = 14
FONT_SIZE_L = 18

STYLESHEET = """
#sectionHeader {
    font-size: 14pt;
    font-weight: bold;
    color: #333;
    margin-top: 10px;
    margin-bottom: 5px;
}

#detailsScrollArea {
    border: none;
    background-color: #fcfcfc;
}

#placeholderLabel {
    font-size: 12pt;
    color: #888;
}

QFrame#answerFrame {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 10px;
    background-color: #fff;
}

QFrame#answerFrame[correct="true"] {
    background-color: #e8f5e9; /* A light green */
    border-color: #a5d6a7;
}

QProgressBar {
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #eee;
}

QProgressBar::chunk {
    background-color: #64b5f6; /* A pleasant blue */
    width: 10px;
    margin: 0.5px;
}
"""
