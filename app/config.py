import sys
from pathlib import Path

from platformdirs import user_data_dir, user_log_dir


def get_base_dir():

    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

LIGHT_DIR = ICONS_DIR / "light"
DARK_DIR = ICONS_DIR / "dark"

APP_NAME = "Listy"

DATA_DIR = Path(user_data_dir(APP_NAME, roaming=True))
LOGS_DIR = Path(user_log_dir(APP_NAME))

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

CONFIG_FILE = DATA_DIR / "config.json"

DEFAULT_SETTINGS = {
    "theme": "light",
    "lang": "ru_RU",
}
