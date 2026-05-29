import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "ui_scale": 1.0
}

def load_settings():

    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)

    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(data):

    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)