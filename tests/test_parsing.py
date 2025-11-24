from doughub.ui.parsing import parse_question_html

ACEP_HTML = """
<html>
<body>
    <div class="questionStem">
        <p>A 37-year-old Black woman presents with bilateral eye redness.</p>
    </div>
    <div class="choices">
        <li class="paper-shadow incorrect">
            <label>Admit to hospital</label>
            <div class="peer-percent">8%</div>
        </li>
        <li class="paper-shadow correct">
            <label>Discharge home</label>
            <div class="peer-percent">50%</div>
        </li>
    </div>
    <div class="exam-reasoning">
        <p>This is the explanation.</p>
    </div>
</body>
</html>
"""

MKSAP_HTML = """
<html>
<body>
    <section class="q_info">
        <p>A 62-year-old woman is evaluated.</p>
    </section>
    <section class="q_mcq">
        <div class="option">
            <span class="letter">A</span>
            <span class="answer-text">Azithromycin</span>
            <div class="stats">10%</div>
        </div>
        <div class="option">
            <span class="letter">C</span>
            <span class="answer-text">Fluid replacement</span>
            <div class="stats">82%</div>
        </div>
    </section>
    <section class="answer">
        <p>Correct Answer: C</p>
        <p>Fluid replacement is the most appropriate treatment.</p>
    </section>
</body>
</html>
"""

def test_parse_acep() -> None:
    metadata = {'url': 'http://example.com'}
    result = parse_question_html(ACEP_HTML, metadata)

    assert "A 37-year-old Black woman" in result['question_html']
    assert len(result['answers']) == 2
    assert result['answers'][0]['text'] == "Admit to hospital"
    assert result['answers'][0]['is_correct'] is False
    assert result['answers'][0]['peer_percentage'] == 8.0
    assert result['answers'][1]['text'] == "Discharge home"
    assert result['answers'][1]['is_correct'] is True
    assert "This is the explanation" in result['explanation_html']

def test_parse_mksap() -> None:
    metadata = {'url': 'http://example.com'}
    result = parse_question_html(MKSAP_HTML, metadata)

    assert "A 62-year-old woman" in result['question_html']
    assert len(result['answers']) == 2
    assert result['answers'][0]['text'] == "Azithromycin"
    assert result['answers'][0]['letter'] == "A"
    assert result['answers'][0]['is_correct'] is False
    assert result['answers'][1]['text'] == "Fluid replacement"
    assert result['answers'][1]['letter'] == "C"
    assert result['answers'][1]['is_correct'] is True
    assert "Fluid replacement is the most appropriate treatment" in result['explanation_html']

def test_parse_empty() -> None:
    result = parse_question_html("", {})
    assert result['question_html'] == '<i>No content available.</i>'
    assert result['answers'] == []

def test_image_resolution() -> None:
    html = """
    <div class="questionStem">
        <img src="image.jpg">
    </div>
    """
    metadata = {'url': 'http://example.com/base/'}
    result = parse_question_html(html, metadata)

    assert "http://example.com/base/image.jpg" in result['question_html']
    assert "http://example.com/base/image.jpg" in result['images']
