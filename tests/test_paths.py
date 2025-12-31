"""
Unit tests for path resolution in settings module
"""
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from clipper_agent.settings import get_project_root

def test_get_project_root_source():
    """Test get_project_root when running from source"""
    with patch("sys.frozen", False, create=True):
        root = get_project_root()
        # Should be parent.parent of settings.py
        expected = Path(__file__).resolve().parent.parent / "clipper_agent"
        # settings.py is in clipper_agent/settings.py
        # root is parent of clipper_agent which is repository root

        # Actually my test file is tests/test_paths.py (to be created)
        # But here I am importing get_project_root from clipper_agent.settings
        # So it uses __file__ of clipper_agent/settings.py

        # clipper_agent/settings.py
        # parent -> clipper_agent
        # parent.parent -> root

        assert root.name != "clipper_agent" # It should be the repo root
        assert (root / "clipper_agent").exists()

def test_get_project_root_frozen():
    """Test get_project_root when running as PyInstaller executable"""
    mock_executable = "/path/to/dist/ClipperAgent"

    with patch("sys.frozen", True, create=True), \
         patch("sys.executable", mock_executable):

        root = get_project_root()
        assert root == Path("/path/to/dist")
