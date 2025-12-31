"""
Unit tests for settings module
"""
import os
import json
import pytest
from unittest.mock import patch
from clipper_agent import settings

@pytest.fixture
def mock_settings_file(tmp_path):
    """Create a temporary settings file and patch the path in settings module"""
    d = tmp_path / "ClipperAgent"
    d.mkdir()
    f = d / "settings.json"

    # Patch the get_app_data_dir to return our temp dir
    with patch("clipper_agent.settings.get_app_data_dir", return_value=d):
        yield f

def test_load_settings_empty(mock_settings_file):
    """Test loading when file does not exist"""
    # File not created yet
    loaded = settings.load_settings()
    assert loaded["prompts"] == []
    assert loaded["default_prompt_name"] is None
    assert loaded["log_level"] == "INFO"

def test_load_settings_valid(mock_settings_file):
    """Test loading a valid settings file"""
    data = {
        "prompts": [{"name": "test", "content": "foo", "model": "bar"}],
        "default_prompt_name": "test",
        "log_level": "DEBUG"
    }
    mock_settings_file.write_text(json.dumps(data), encoding="utf-8")

    loaded = settings.load_settings()
    assert len(loaded["prompts"]) == 1
    assert loaded["prompts"][0]["name"] == "test"
    assert loaded["default_prompt_name"] == "test"
    assert loaded["log_level"] == "DEBUG"

def test_save_settings(mock_settings_file):
    """Test saving settings"""
    data = {
        "prompts": [{"name": "saved", "content": "content", "model": "model"}],
        "default_prompt_name": None,
        "log_level": "INFO"
    }
    settings.save_settings(data)

    assert mock_settings_file.exists()
    with open(mock_settings_file, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved["prompts"][0]["name"] == "saved"

def test_add_prompt(mock_settings_file):
    """Test adding a prompt"""
    settings.add_prompt("new_prompt", "content", "model")

    loaded = settings.load_settings()
    assert len(loaded["prompts"]) == 1
    assert loaded["prompts"][0]["name"] == "new_prompt"

    # Test duplicate check
    result = settings.add_prompt("new_prompt", "content2", "model2")
    assert result is False

    loaded = settings.load_settings()
    assert len(loaded["prompts"]) == 1 # Should not change

def test_update_prompt(mock_settings_file):
    """Test updating a prompt"""
    settings.add_prompt("p1", "c1", "m1")

    # Update existing
    result = settings.update_prompt("p1", "p1_updated", "c1_upd", "m1_upd")
    assert result is True

    loaded = settings.load_settings()
    assert loaded["prompts"][0]["name"] == "p1_updated"
    assert loaded["prompts"][0]["content"] == "c1_upd"

    # Rename with default prompt update
    settings.set_default_prompt("p1_updated")
    result = settings.update_prompt("p1_updated", "p1_final", "c", "m")

    loaded = settings.load_settings()
    assert loaded["default_prompt_name"] == "p1_final"

def test_delete_prompt(mock_settings_file):
    """Test deleting a prompt"""
    settings.add_prompt("p1", "c1", "m1")
    settings.set_default_prompt("p1")

    result = settings.delete_prompt("p1")
    assert result is True

    loaded = settings.load_settings()
    assert len(loaded["prompts"]) == 0
    assert loaded["default_prompt_name"] is None

def test_get_prompt_by_name(mock_settings_file):
    """Test getting prompt by name"""
    settings.add_prompt("p1", "c1", "m1")

    prompt = settings.get_prompt_by_name("p1")
    assert prompt["name"] == "p1"

    prompt = settings.get_prompt_by_name("nonexistent")
    assert prompt is None

def test_get_prompt_legacy(mock_settings_file):
    """Test legacy get_prompt raises ValueError"""
    settings.add_prompt("p1", "c1", "m1")

    prompt = settings.get_prompt("p1")
    assert prompt["name"] == "p1"

    with pytest.raises(ValueError):
        settings.get_prompt("nonexistent")

def test_set_log_level(mock_settings_file):
    """Test setting log level"""
    settings.set_log_level("DEBUG")
    loaded = settings.load_settings()
    assert loaded["log_level"] == "DEBUG"

    with pytest.raises(ValueError):
        settings.set_log_level("INVALID")
