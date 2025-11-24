"""Advanced HTML parsing and cleaning for DougHub.

This module is responsible for taking raw HTML extracted from question sources
and converting it into a clean, standardized, and semantically correct format
that can be reliably displayed in the UI.
"""

import logging
from collections.abc import Callable
from typing import Any, cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

logger = logging.getLogger(__name__)


class HtmlCleaner:
    """A class to recursively clean and rebuild HTML from BeautifulSoup tags."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.images: list[str] = []

    def _is_significant_tag(self, tag: Tag) -> bool:
        """Determine if a tag should be preserved."""
        # Keep structural tags and formatting tags
        return tag.name in [
            'p', 'ul', 'ol', 'li', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'table', 'tr', 'td', 'th', 'thead', 'tbody'
        ]

    def _clean_and_rebuild_html(self, element: PageElement) -> str:
        """
        Recursively processes a BeautifulSoup element to generate clean HTML.
        - Unwraps insignificant tags (divs, spans).
        - Preserves structural tags (p, li, etc.).
        - Converts images to absolute URLs.
        - Rebuilds the HTML string.
        """
        if isinstance(element, NavigableString):
            return str(element)

        if not isinstance(element, Tag):
            return ''

        # Handle images separately to capture URLs
        if element.name == 'img':
            src = element.get('src')
            if isinstance(src, str):
                abs_url = urljoin(self.base_url, src)
                if abs_url not in self.images:
                    self.images.append(abs_url)
                # Create a new, clean img tag
                return f'<img src="{abs_url}" style="max-width: 100%; height: auto;" />'
            return ''

        # If the tag is not significant, process its children and join them.
        if not self._is_significant_tag(element):
            # Treat divs/spans as block separators if they contain block elements
            # or have significant line breaks.
            content = "".join(self._clean_and_rebuild_html(child) for child in element.contents)
            if any(child.name in ['p', 'ul', 'ol', 'div'] for child in element.find_all(recursive=False)):
                 return f'<div>{content}</div>' # Use div to maintain block context
            return content

        # Re-create the significant tag with cleaned children
        children_html = "".join(self._clean_and_rebuild_html(child) for child in element.contents)

        # Add some basic inline styling for lists to improve readability
        if element.name in ['ul', 'ol']:
            return f'<{element.name} style="margin-left: 20px; padding-left: 10px;">{children_html}</{element.name}>'

        return f'<{element.name}>{children_html}</{element.name}>'


def _parse_with_cleaner(soup: Tag, cleaner: HtmlCleaner) -> str:
    """Run the cleaner on a BeautifulSoup Tag and post-process the result."""
    if not soup:
        return ""

    # We remove unwanted tags before processing.
    for tag in soup(['script', 'style', 'link', 'meta', 'button', 'input']):
        tag.decompose()

    cleaned_html = cleaner._clean_and_rebuild_html(soup)

    # Wrap the entire content in a div with base styling for consistent rendering
    final_html = f"""
<div style="font-family: sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
{cleaned_html}
</div>
"""

    return final_html

# --- Source-Specific Parsers ---

def _parse_acep_content(soup: BeautifulSoup, cleaner: HtmlCleaner) -> dict[str, Any]:
    """Parser for ACEP content."""
    result: dict[str, Any] = {
        'question_html': '<i>Question not found.</i>',
        'answers': [],
        'explanation_html': '<i>Explanation not found.</i>'
    }

    # Question
    stem = soup.select_one('div.questionStem')
    if stem:
        result['question_html'] = _parse_with_cleaner(stem, cleaner)

    # Answers
    choices_container = soup.select_one('div.choices')
    if choices_container:
        choices = choices_container.select('li.paper-shadow')
        for choice in choices:
            text_el = choice.select_one('label')
            text = text_el.get_text(strip=True) if text_el else choice.get_text(strip=True)

            choice_classes = cast(list[str], choice.get('class') or [])
            is_correct = 'correct' in choice_classes

            peer_percentage = None
            peer_el = choice.select_one('.peer-percent')
            if peer_el:
                try:
                    peer_text = peer_el.get_text(strip=True).replace('%', '')
                    peer_percentage = float(peer_text)
                except (ValueError, TypeError):
                    pass

            result['answers'].append({
                'text': text, 'is_correct': is_correct, 'peer_percentage': peer_percentage
            })

    # Explanation
    explanation = soup.select_one('div.exam-reasoning, div.reasoning')
    if explanation:
        result['explanation_html'] = _parse_with_cleaner(explanation, cleaner)

    return result

def _parse_mksap_content(soup: BeautifulSoup, cleaner: HtmlCleaner) -> dict[str, Any]:
    """Parser for MKSAP content."""
    result: dict[str, Any] = {
        'question_html': '<i>Question not found.</i>',
        'answers': [],
        'explanation_html': '<i>Explanation not found.</i>'
    }

    # Question
    question_content = soup.select_one('section.q_info, div.question-content')
    if question_content:
        # Exclude answer choices from the question block if they are nested
        for answer_block in question_content.select('section.q_mcq, div.choices'):
            answer_block.decompose()
        result['question_html'] = _parse_with_cleaner(question_content, cleaner)

    # Answers
    q_mcq = soup.select_one('section.q_mcq')
    if q_mcq:
        options = q_mcq.select('div.option')
        for option in options:
            text = (option.select_one('span.answer-text, span.text') or option).get_text(strip=True)
            letter_el = option.select_one('div.bubble, span.letter')
            letter = letter_el.get_text(strip=True) if letter_el else ""

            # Check for correctness using class 'r_a' (Right Answer)
            # Also checking 's_a' (Selected Answer) combined with 'r_a' just in case,
            # but 'r_a' seems to be the definitive marker for the correct answer key.
            classes = cast(list[str], option.get('class') or [])
            is_correct = 'r_a' in classes

            peer_percentage = None
            peer_el = option.select_one('div.stats, div.peer')
            if peer_el:
                try:
                    peer_text = peer_el.get_text(strip=True).replace('%', '')
                    peer_percentage = float(peer_text)
                except (ValueError, TypeError):
                    pass

            result['answers'].append({
                'text': text, 'is_correct': is_correct, 'peer_percentage': peer_percentage, 'letter': letter
            })

    # Explanation
    explanation = soup.select_one('section.answer, div.exposition')
    if explanation:
        result['explanation_html'] = _parse_with_cleaner(explanation, cleaner)

        # Fallback: If no answer was marked correct via classes, try regex on explanation
        if not any(ans['is_correct'] for ans in result['answers']):
            import re
            match = re.search(r'Correct Answer:\s*([A-Z])', explanation.get_text())
            if match:
                correct_letter = match.group(1)
                for ans in result['answers']:
                    if ans.get('letter') == correct_letter:
                        ans['is_correct'] = True

    return result

def _parse_generic_content(soup: BeautifulSoup, cleaner: HtmlCleaner) -> dict[str, Any]:
    """A generic fallback parser."""
    return {
        'question_html': _parse_with_cleaner(soup.body, cleaner) if soup.body else '<i>No content available.</i>',
        'answers': [],
        'explanation_html': '',
    }

# --- Main Entry Point ---

def parse_question_html(raw_html: str, raw_metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Parses raw question HTML to extract, clean, and standardize content.
    """
    if not raw_html:
        return {
            'question_html': '<i>No content available.</i>', 'answers': [],
            'explanation_html': '<i>No explanation available.</i>', 'images': []
        }

    soup = BeautifulSoup(raw_html, 'html.parser')
    base_url = raw_metadata.get('url', '')
    cleaner = HtmlCleaner(base_url=base_url)

    # Determine the parser to use
    parser: Callable[[BeautifulSoup, HtmlCleaner], dict[str, Any]]
    if soup.select_one('div.questionStem'):
        parser = _parse_acep_content
        logger.debug("Using ACEP parser.")
    elif soup.select_one('section.q_info, section.q_mcq'):
        parser = _parse_mksap_content
        logger.debug("Using MKSAP parser.")
    else:
        parser = _parse_generic_content
        logger.warning("Unknown source format. Using generic parser.")

    # Parse content
    parsed_data = parser(soup, cleaner)

    # Consolidate images from the cleaner instance
    parsed_data['images'] = cleaner.images

    return parsed_data
