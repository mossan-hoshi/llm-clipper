"""
Unit tests for gemini_api module
"""
import pytest
from unittest.mock import patch, MagicMock
from clipper_agent.gemini_api import generate_text, load_api_settings

@patch("clipper_agent.gemini_api.genai")
@patch("clipper_agent.gemini_api.load_api_settings")
def test_generate_text_success(mock_load_api_settings, mock_genai):
    """Test successful text generation"""
    # Setup mocks
    mock_load_api_settings.return_value = ("fake_api_key", [])

    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Generated text"
    mock_model.generate_content.return_value = mock_response

    mock_genai.GenerativeModel.return_value = mock_model

    # Call function
    result = generate_text("Prompt", "gemini-pro")

    # Verify
    assert result == "Generated text"
    mock_genai.configure.assert_called_with(api_key="fake_api_key")
    mock_genai.GenerativeModel.assert_called_with("gemini-pro")
    mock_model.generate_content.assert_called_with("Prompt")

@patch("clipper_agent.gemini_api.load_api_settings")
def test_generate_text_no_api_key(mock_load_api_settings):
    """Test behavior when API key is missing (simulated by load_api_settings raising)"""
    mock_load_api_settings.side_effect = ValueError("GEMINI_API_KEYが設定されていません")

    with pytest.raises(ValueError, match="GEMINI_API_KEYが設定されていません"):
        generate_text("Prompt", "gemini-pro")

@patch("clipper_agent.gemini_api.genai")
@patch("clipper_agent.gemini_api.load_api_settings")
def test_generate_text_api_error(mock_load_api_settings, mock_genai):
    """Test handling of API errors"""
    mock_load_api_settings.return_value = ("fake_api_key", [])

    mock_model = MagicMock()
    # Simulate API error
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_genai.GenerativeModel.return_value = mock_model

    # Note: generate_text wraps exception in ValueError with "Gemini APIの呼び出しに失敗しました: ..."
    with pytest.raises(ValueError, match="Gemini APIの呼び出しに失敗しました: API Error"):
        generate_text("Prompt", "gemini-pro")
