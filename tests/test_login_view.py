import flet as ft
import sys
import os

# Ensure src is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.login_view import LoginView
from src.config import THEME
from src.core.utils import get_resource_path

def main(page: ft.Page):
    page.title = "CryptoVault"
    page.bgcolor = THEME.colors.bg
    
    # 1. Definimos las dimensiones ideales unificadas para toda la app
    # Un tamaño de 1050x750 es perfecto para un dashboard con sidebar + tabla + panel lateral
    page.window.full_screen = True
    # Alineación de los contenidos internos de las vistas
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Create the view instance
    login = LoginView(page)
    
    # In a Sandbox test, we add the controls directly to the page
    page.add(*login.controls)
    page.update()

if __name__ == "__main__":
    # Definimos la ruta de assets relativa a este archivo de test
    assets_path = get_resource_path("assets")
    
    # Standard way to run Flet apps
    ft.run(main=main, assets_dir=assets_path)