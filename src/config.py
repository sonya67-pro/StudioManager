"""Глобальные настройки приложения StudioManager."""

from pathlib import Path

APP_NAME: str = "StudioManager"
APP_VERSION: str = "0.1.0"

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DB_PATH: Path = BASE_DIR / "studio.db"
BACKUPS_DIR: Path = BASE_DIR / "backups"
