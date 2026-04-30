import sys
from pathlib import Path

from platformdirs import user_data_dir, user_log_dir


def get_base_dir() -> Path:

    if getattr(sys, "frozen", False):

        # PyInstaller onefile extracts app to temporary _MEIPASS directory.
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)

        # PyInstaller onedir: assets can be placed near exe or in _internal.
        exe_dir = Path(sys.executable).parent
        if (exe_dir / "assets").exists():
            return exe_dir

        internal_dir = exe_dir / "_internal"
        if (internal_dir / "assets").exists():
            return internal_dir

        # Fallback to exe dir to preserve previous behavior.
        return exe_dir

    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
LIGHT_DIR = ICONS_DIR / "light"
DARK_DIR = ICONS_DIR / "dark"

LOCALES_DIR = BASE_DIR / "locales"

APP_NAME = "Listy"
DATA_DIR = Path(user_data_dir(APP_NAME, roaming=True))
LOGS_DIR = Path(user_log_dir(APP_NAME))

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"

DEFAULT_SETTINGS = {
    "theme": "light",
    "lang": "ru_RU",
}
