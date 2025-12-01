import json
import os
import sys
from importlib import reload
from pathlib import Path
import types

import pytest


def prepare_settings(tmp_path: Path):
    os.environ["APPDATA"] = str(tmp_path)

    from clipper_agent import settings as settings_module

    reload(settings_module)
    settings_path = Path(settings_module.SETTINGS_FILE)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_data = {
        "default_prompt_name": "demo",
        "prompts": [
            {
                "name": "demo",
                "content": "Echo: ${clipboard}",
                "model": "fake-model",
            }
        ],
    }
    settings_path.write_text(json.dumps(settings_data, ensure_ascii=False), encoding="utf-8")
    return settings_module


def test_main_flow_with_mocked_llm(monkeypatch, tmp_path, capsys):
    settings_module = prepare_settings(tmp_path / "appdata")

    sys.modules.setdefault(
        "pyperclip", types.SimpleNamespace(paste=lambda: "", copy=lambda text: None)
    )
    dotenv_module = types.ModuleType("dotenv")
    dotenv_module.load_dotenv = lambda *args, **kwargs: None
    sys.modules.setdefault("dotenv", dotenv_module)

    google_pkg = sys.modules.setdefault("google", types.ModuleType("google"))
    genai_module = types.ModuleType("google.generativeai")
    genai_module.configure = lambda **kwargs: None

    class _DummyModel:
        def __init__(self, model_id):
            self.model_id = model_id

        def generate_content(self, prompt):
            return types.SimpleNamespace(text="")

    genai_module.GenerativeModel = _DummyModel
    sys.modules.setdefault("google.generativeai", genai_module)
    setattr(google_pkg, "generativeai", genai_module)

    import ClipperAgent

    reload(ClipperAgent)

    clipboard_values = {}

    monkeypatch.setattr(
        "clipper_agent.clipboard.get_clipboard_text", lambda: "clipboard text"
    )
    monkeypatch.setattr(
        "ClipperAgent.get_clipboard_text", lambda: "clipboard text"
    )
    monkeypatch.setattr(
        "clipper_agent.clipboard.set_clipboard_text",
        lambda text: clipboard_values.setdefault("content", text),
    )
    monkeypatch.setattr(
        "ClipperAgent.set_clipboard_text",
        lambda text: clipboard_values.setdefault("content", text),
    )
    monkeypatch.setattr(
        "clipper_agent.gemini_api.generate_text",
        lambda prompt, model_id="gemini-pro": f"[{model_id}] {prompt}",
    )
    monkeypatch.setattr(
        "ClipperAgent.generate_text",
        lambda prompt, model_id="gemini-pro": f"[{model_id}] {prompt}",
    )
    monkeypatch.setattr(
        "clipper_agent.notification.show_notification", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "ClipperAgent.show_notification", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(sys, "argv", ["ClipperAgent.py"])

    ClipperAgent.main()

    assert clipboard_values.get("content") == "[fake-model] Echo: clipboard text"
    out = capsys.readouterr().out
    assert "デフォルトプロンプト 'demo'" in out
    assert "クリップボードからテキストを取得しました" in out
    assert "ClipperAgentを起動しました" in out
    assert "結果をクリップボードにコピーしました" in out

    assert Path(settings_module.SETTINGS_FILE).exists()
