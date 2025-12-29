"""
ロギングモジュール
ログの設定と記録を行う機能を提供します。
"""

import os
import logging
from pathlib import Path
from clipper_agent.settings import get_settings

def setup_logging():
    """
    ロギングの設定を行います。
    ログファイルはユーザーのアプリケーションデータディレクトリに保存されます。
    
    Returns:
        logging.Logger: 設定済みのロガーオブジェクト
    """
    # アプリケーションデータディレクトリ
    app_data_dir = Path(os.getenv('APPDATA')) / 'ClipperAgent'
    os.makedirs(app_data_dir, exist_ok=True)
    
    # ログファイルパス
    log_file = app_data_dir / 'ClipperAgent.log'
    
    # 設定からログレベルを取得
    try:
        settings = get_settings()
        log_level_str = settings.get('log_level', 'INFO').upper()
    except Exception:
        log_level_str = 'INFO'

    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'ERROR': logging.ERROR
    }
    log_level = level_map.get(log_level_str, logging.INFO)

    # ロガーの設定
    logger = logging.getLogger('ClipperAgent')
    logger.setLevel(log_level)

    # 既存のハンドラーをクリア（重複防止）
    if logger.handlers:
        logger.handlers.clear()
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # フォーマット
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # ハンドラーの追加
    logger.addHandler(file_handler)
    
    return logger
