\
import json
import os
from pathlib import Path

APP_NAME = "ClipperAgent"
SETTINGS_FILE_NAME = "settings.json"

def get_app_data_dir() -> Path:
    app_data_dir = Path(os.getenv("APPDATA", "")) / APP_NAME
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir

def get_settings_file_path() -> Path:
    return get_app_data_dir() / SETTINGS_FILE_NAME

def load_settings() -> dict:
    """設定ファイルを読み込みます。ファイルが存在しない場合は空の辞書を返します。"""
    settings_file = get_settings_file_path()
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # ファイルが不正な場合は空のデータを返すか、エラーを通知する
            return {"prompts": [], "default_prompt_name": None}
    return {"prompts": [], "default_prompt_name": None}

def save_settings(settings_data: dict):
    """設定データをファイルに保存します。"""
    settings_file = get_settings_file_path()
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=4, ensure_ascii=False)

def add_prompt(prompt_name: str, prompt_text: str, model_id: str) -> bool:
    """新しいプロンプトを追加します。"""
    settings = load_settings()
    # 簡単な重複チェック（ステップ5で詳細化）
    # for p in settings.get("prompts", []):
    #     if p["name"] == prompt_name:
    #         return False # 重複あり

    new_prompt = {
        "name": prompt_name,
        "text": prompt_text,
        "model": model_id,
    }
    if "prompts" not in settings or not isinstance(settings["prompts"], list):
        settings["prompts"] = []
    
    settings["prompts"].append(new_prompt)
    save_settings(settings)
    return True

if __name__ == '__main__':
    # テスト用
    print(f"Settings file path: {get_settings_file_path()}")
    
    # 初期設定の作成（テスト）
    initial_settings = {
        "prompts": [
            {"name": "Test Prompt 1", "text": "This is a test prompt.", "model": "gemini-pro"},
        ],
        "default_prompt_name": None
    }
    save_settings(initial_settings)
    print(f"Initial settings saved: {initial_settings}")

    loaded = load_settings()
    print(f"Loaded settings: {loaded}")

    add_prompt("Test Prompt 2", "Another test prompt.", "gemini-flash")
    loaded_after_add = load_settings()
    print(f"Settings after add: {loaded_after_add}")
