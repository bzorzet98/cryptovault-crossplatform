import flet as ft
import sys
import os

# Aseguramos que el path incluya la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.welcome_view import WelcomeView
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
    
    # Instanciamos la vista
    welcome = WelcomeView(page)
    
    # Agregamos los controles al sandbox
    page.add(*welcome.controls)
    page.update()

if __name__ == "__main__":
    # Definimos la ruta de assets relativa a este archivo de test
    assets_path = get_resource_path("assets")
    
    # Verificación rápida del logo en consola para evitar errores de ruta
    logo_check = os.path.join(assets_path, "images/logo1.png")
    print(f"Buscando logo en: {logo_check}")
    print("✅ Logo encontrado" if os.path.exists(logo_check) else "❌ Logo no encontrado")

    ft.app(target=main, assets_dir=assets_path)