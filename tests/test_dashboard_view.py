import flet as ft
import sys
import os

# 1. Aseguramos que Python encuentre la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.dashboard_view import DashboardView
from src.config import THEME

def main(page: ft.Page):
    # Configuración de la ventana para una vista de escritorio pro
    page.title = "Sandbox: Dashboard & Components"
    page.window_width = 1300
    page.window_height = 850
    page.window_min_width = 1000
    page.window_min_height = 700
    page.bgcolor = THEME.colors.bg
    page.padding = 0
    page.spacing = 0

    # Instanciamos la vista principal
    # Nota: Al ser un test, pasamos 'page' directamente
    dash_view = DashboardView(page)
    
    # En Flet, una 'View' tiene una lista de controles. 
    # Para el sandbox, los añadimos directamente a la página.
    page.add(*dash_view.controls)
    
    print("--- Dashboard Sandbox Iniciado ---")
    print("Prueba: Haz clic en los ítems de la lista para ver el cambio en el DetailView.")
    page.update()

if __name__ == "__main__":
    # 2. Ruta de assets (asegúrate de que src/assets exista)
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/assets"))
    
    # Ejecutar la app
    ft.app(target=main, assets_dir=assets_dir)