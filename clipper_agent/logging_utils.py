"""
ロギングモジュール
ログの設定と記録を行う機能を提供します。
"""

import os
import logging
from pathlib import Path

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
    
    # ロガーの設定
    logger = logging.getLogger('ClipperAgent')
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # フォーマット
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # ハンドラーの追加
    logger.addHandler(file_handler)
    
    return logger
