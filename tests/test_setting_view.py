import flet as ft
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.settings_view import SettingsView
from src.config import THEME

def main(page: ft.Page):
    page.title = "Sandbox: Settings View"
    page.window_width = 1200
    page.window_height = 850
    page.bgcolor = THEME.colors.bg
    page.padding = 0

    settings = SettingsView(page)
    page.add(*settings.controls)
    page.update()

if __name__ == "__main__":
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/assets"))
    ft.app(target=main, assets_dir=assets_dir)