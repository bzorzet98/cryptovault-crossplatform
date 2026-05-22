"""
theme.py
────────
Global UI scaling, fonts, colors and icon loader.
"""
import customtkinter as ctk
from PIL import Image
import os

from src.ui.settings_manager import (
    load_settings,
    save_settings
)

BASE_DIR = os.path.dirname(__file__)

CURRENT_THEME = "dark"

UI_SCALE = 1.0

THEMES = {

    "dark": {

        "bg": "#151515",
        "bg2": "#1e1e1e",

        "sidebar": "#161616",

        "card": "#252525",

        "accent": "#2c8558",
        "accent_hover": "#1e5c3d",

        "danger": "#a33030",
        "danger_hover": "#7a2020",

        "text": "#f2f2f2",
        "text_secondary": "#aaaaaa",

        "border": "#3a3a3a",

        "hover": "#333333",
        "grey": "#888888"
    },

    "light": {

        "bg": "#f3f3f3",
        "bg2": "#ffffff",

        "sidebar": "#e8e8e8",

        "card": "#ffffff",

        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",

        "danger": "#dc2626",
        "danger_hover": "#b91c1c",

        "text": "#111111",
        "text_secondary": "#555555",

        "border": "#cccccc",

        "hover": "#dddddd",
        "grey": "#888888"
    },

    "oled": {

        "bg": "#000000",
        "bg2": "#050505",

        "sidebar": "#050505",

        "card": "#101010",

        "accent": "#00c853",
        "accent_hover": "#009624",

        "danger": "#ff3b30",
        "danger_hover": "#d63028",

        "text": "#ffffff",
        "text_secondary": "#888888",

        "border": "#222222",

        "hover": "#1b1b1b",
        "grey": "#888888"
    }
}

def c(key: str):
    return THEMES[CURRENT_THEME][key]

def set_ui_scale(scale: float):
    global UI_SCALE

    UI_SCALE = scale

    ctk.set_widget_scaling(scale)


# ═════════════════════════════════════════════════════════════
# FONT HELPERS
# ═════════════════════════════════════════════════════════════
def font(size, weight="normal"):
    return ("Segoe UI", int(size * UI_SCALE), weight)


# ═════════════════════════════════════════════════════════════
# ICON HELPERS
# ═════════════════════════════════════════════════════════════
def icon_size(size):

    if isinstance(size, tuple):

        return (
            int(size[0] * UI_SCALE),
            int(size[1] * UI_SCALE)
        )

    s = int(size * UI_SCALE)

    return (s, s)


def load_icon(name, size=(18,18)):

    base = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    path = os.path.join(base, "icons", name)

    if not os.path.exists(path):
        return None

    return ctk.CTkImage(
        Image.open(path),
        size=icon_size(size)
    )
    
def load_user_preferences():

    global CURRENT_THEME
    global UI_SCALE

    s = load_settings()

    CURRENT_THEME = s.get("theme", "dark")
    UI_SCALE = s.get("ui_scale", 1.0)

    ctk.set_widget_scaling(UI_SCALE)
    ctk.set_window_scaling(UI_SCALE)

    if CURRENT_THEME == "light":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")
        
def set_theme(name):

    global CURRENT_THEME

    if name not in THEMES:
        return

    CURRENT_THEME = name

    if name == "light":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

    s = load_settings()

    s["theme"] = name

    save_settings(s)
    
def set_scale(scale):

    global UI_SCALE

    UI_SCALE = scale

    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)

    s = load_settings()

    s["ui_scale"] = scale

    save_settings(s)