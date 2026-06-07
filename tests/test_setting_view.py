import flet as ft
import sys
import os

# Aseguramos que Python encuentre la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.settings_view import SettingsView
from src.config import THEME

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Sandbox: Settings View"
    page.window_width = 1200
    page.window_height = 850
    page.bgcolor = THEME.colors.bg
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    # ==========================================
    # --- CALLBACKS DE ACCIONES (Settings) ---
    # ==========================================
    def on_sync_toggle(e):
        print(f"[TEST] Sincronización en la nube cambiada a: {e.control.value}")

    def on_theme_change(e):
        selected_theme = e.control.value
        print(f"[TEST] Tema cambiado a: {selected_theme}")
        # Efecto visual real en el sandbox
        page.theme_mode = ft.ThemeMode.DARK if selected_theme == "dark" else ft.ThemeMode.LIGHT
        page.update()

    def on_export_click(e):
        print("[TEST] Acción solicitada: Exportar bóveda a JSON.")

    def on_delete_click(e):
        print("[TEST] ¡ALERTA! Acción solicitada: Eliminar bóveda permanentemente.")


    # ==========================================
    # --- CALLBACKS DE NAVEGACIÓN (Sidebar) ---
    # ==========================================
    # En tu app final, aquí usarías page.go("/ruta")
    
    def handle_nav_all(e): print("[ROUTER] Navegando a: Todas las contraseñas (/all)")
    def handle_nav_fav(e): print("[ROUTER] Navegando a: Favoritos (/favorites)")
    def handle_nav_shared(e): print("[ROUTER] Navegando a: Compartidos (/shared)")
    def handle_nav_security(e): print("[ROUTER] Navegando a: Panel de Seguridad (/security)")
    def handle_nav_notes(e): print("[ROUTER] Navegando a: Notas Seguras (/notes)")
    def handle_nav_settings(e): print("[ROUTER] Ya estás en Configuración (/settings)")


    # ==========================================
    # --- INSTANCIAR LA VISTA ---
    # ==========================================
    
    settings = SettingsView(
        page=page,
        # Acciones propias de la vista
        on_sync_change=on_sync_toggle,
        on_theme_change=on_theme_change,
        on_export_click=on_export_click,
        on_delete_click=on_delete_click,
        # Acciones de navegación para el Sidebar
        on_all_click=handle_nav_all,
        on_fav_click=handle_nav_fav,
        on_shared_click=handle_nav_shared,
        on_security_click=handle_nav_security,
        on_notes_click=handle_nav_notes,
        on_settings_click=handle_nav_settings
    )
    
    page.add(*settings.controls)
    page.update()

if __name__ == "__main__":
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/assets"))
    print("--- Settings View Sandbox Iniciado ---")
    print("Prueba hacer click en los botones del menú y revisar esta consola.")
    ft.app(target=main, assets_dir=assets_dir)