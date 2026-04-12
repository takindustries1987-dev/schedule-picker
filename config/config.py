"""
処理内容:
- アプリ設定の取得場所

使い方:
- 他のモジュールから import して使う
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")


settings = Settings()

