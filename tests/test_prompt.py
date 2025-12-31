"""
Unit tests for prompt module
"""
from clipper_agent.prompt import build_prompt

def test_build_prompt_basic():
    """Test basic substitution"""
    template = "Translate this: ${clipboard}"
    clipboard = "Hello World"
    expected = "Translate this: Hello World"
    assert build_prompt(template, clipboard) == expected

def test_build_prompt_no_substitution():
    """Test when no placeholder is present"""
    template = "Just a prompt"
    clipboard = "Hello World"
    expected = "Just a prompt"
    assert build_prompt(template, clipboard) == expected

def test_build_prompt_multiple_substitutions():
    """Test multiple occurrences of placeholder"""
    template = "${clipboard} -> ${clipboard}"
    clipboard = "A"
    expected = "A -> A"
    assert build_prompt(template, clipboard) == expected

def test_build_prompt_newline_handling():
    """Test that \\n is converted to actual newline"""
    template = "Line 1\\nLine 2: ${clipboard}"
    clipboard = "Content"
    expected = "Line 1\nLine 2: Content"
    assert build_prompt(template, clipboard) == expected

def test_build_prompt_empty_clipboard():
    """Test with empty clipboard content"""
    template = "Content: ${clipboard}"
    clipboard = ""
    expected = "Content: "
    assert build_prompt(template, clipboard) == expected
