"""
設定ファイル操作モジュール
settings.jsonからプロンプト情報を読み込む機能を提供します。
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# アプリケーションデータディレクトリパス
APP_NAME = "ClipperAgent"
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
SETTINGS_FILE_NAME = "settings.json"
SETTINGS_FILE = os.path.join(APP_DATA_DIR, SETTINGS_FILE_NAME)

def get_app_data_dir() -> Path:
    """アプリケーションデータディレクトリを取得（作成）する"""
    app_data_dir = Path(APP_DATA_DIR)
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir

def get_project_root() -> Path:
    """プロジェクトルート（または実行ファイルのディレクトリ）を取得する"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでパッケージ化されている場合
        return Path(sys.executable).parent
    else:
        # ソースコード実行の場合、プロジェクトルートを返す
        # settings.pyは clipper_agent/settings.py にあるので、parent.parent
        return Path(__file__).resolve().parent.parent

def get_settings_file_path() -> Path:
    """設定ファイルのパスを取得する"""
    return get_app_data_dir() / SETTINGS_FILE_NAME

def _normalize_prompt(prompt: dict) -> dict:
    """プロンプト辞書のキーを現在の仕様に揃える"""
    if "content" not in prompt and "text" in prompt:
        prompt["content"] = prompt.get("text", "")
    return {
        "name": prompt.get("name", ""),
        "content": prompt.get("content", ""),
        "model": prompt.get("model", ""),
    }

def load_settings() -> dict:
    """
    設定ファイルを読み込みます。
    ファイルが存在しない、または不正な場合はデフォルト値を返します。
    """
    settings_file = get_settings_file_path()
    default = {"prompts": [], "default_prompt_name": None, "log_level": "INFO"}
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                prompts = loaded.get("prompts", []) if isinstance(loaded, dict) else []
                normalized_prompts = [_normalize_prompt(p) for p in prompts if isinstance(p, dict)]
                return {
                    "prompts": normalized_prompts,
                    "default_prompt_name": loaded.get("default_prompt_name"),
                    "log_level": loaded.get("log_level", "INFO"),
                }
        except json.JSONDecodeError:
            return default
    return default

def save_settings(settings_data: dict):
    """設定データをファイルに保存します。"""
    settings_file = get_settings_file_path()
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=4, ensure_ascii=False)

# 互換性のためのエイリアス
get_settings = load_settings

def add_prompt(prompt_name: str, prompt_text: str, model_id: str) -> bool:
    """新しいプロンプトを追加します。"""
    settings = load_settings()

    for prompt in settings.get("prompts", []):
        if prompt.get("name") == prompt_name:
            return False  # 重複あり

    new_prompt = {
        "name": prompt_name,
        "content": prompt_text,
        "model": model_id,
    }
    if "prompts" not in settings or not isinstance(settings["prompts"], list):
        settings["prompts"] = []

    settings["prompts"].append(new_prompt)
    save_settings(settings)
    return True

def update_prompt(original_name: str, prompt_name: str, prompt_text: str, model_id: str) -> bool:
    """既存のプロンプトを更新します。"""
    settings = load_settings()

    # 名前変更時の重複チェック
    for prompt in settings.get("prompts", []):
        if prompt.get("name") == prompt_name and prompt_name != original_name:
            return False

    for i, prompt in enumerate(settings.get("prompts", [])):
        if prompt.get("name") == original_name:
            settings["prompts"][i] = {
                "name": prompt_name,
                "content": prompt_text,
                "model": model_id,
            }

            if settings.get("default_prompt_name") == original_name:
                settings["default_prompt_name"] = prompt_name

            save_settings(settings)
            return True
    return False

def delete_prompt(prompt_name: str) -> bool:
    """プロンプトを削除します。"""
    settings = load_settings()
    initial_count = len(settings.get("prompts", []))

    settings["prompts"] = [p for p in settings.get("prompts", []) if p.get("name") != prompt_name]

    if settings.get("default_prompt_name") == prompt_name:
        settings["default_prompt_name"] = None

    save_settings(settings)
    return len(settings.get("prompts", [])) < initial_count

def get_prompt_by_name(prompt_name: str) -> dict:
    """名前を指定してプロンプト情報を取得します。"""
    settings = load_settings()
    for prompt in settings.get("prompts", []):
        if prompt.get("name") == prompt_name:
            return prompt
    # 互換性のため、見つからない場合はNoneを返すが、
    # 古いget_promptはValueErrorを投げていた。
    # ここではNoneを返し、呼び出し元で処理するか、
    # 古いget_prompt関数を別途定義する。
    return None

def get_prompt(prompt_name: str) -> dict:
    """
    指定されたプロンプト名に対応するプロンプト情報を取得します（旧API互換）。
    
    Raises:
        ValueError: 指定されたプロンプト名が存在しない場合
    """
    prompt = get_prompt_by_name(prompt_name)
    if prompt is None:
        raise ValueError(f"指定されたプロンプト '{prompt_name}' が見つかりません。")
    return prompt

def set_default_prompt(prompt_name: Optional[str]) -> None:
    """デフォルトプロンプト名を設定または解除する"""
    settings = load_settings()

    if prompt_name:
        if not any(p.get("name") == prompt_name for p in settings.get("prompts", [])):
            raise ValueError("指定されたプロンプトが存在しません。")
        settings["default_prompt_name"] = prompt_name
    else:
        settings["default_prompt_name"] = None

    save_settings(settings)

def set_log_level(level: str) -> None:
    """ログレベルを設定する"""
    valid_levels = ["DEBUG", "INFO", "ERROR"]
    if level not in valid_levels:
        raise ValueError(f"無効なログレベルです: {level}. 有効な値: {', '.join(valid_levels)}")

    settings = load_settings()
    settings["log_level"] = level
    save_settings(settings)

def load_available_models() -> List[str]:
    """.envからAVAILABLE_MODELSを読み込み、リストで返す"""
    # プロジェクトルート/.env -> APPDATA/.env の順で検索
    env_paths = [
        get_project_root() / ".env",
        get_app_data_dir() / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            models = os.getenv("AVAILABLE_MODELS", "")
            if models:
                return [m.strip() for m in models.split(",") if m.strip()]
            return []

    return []
