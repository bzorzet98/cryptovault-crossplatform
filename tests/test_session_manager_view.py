import flet as ft
import sys
import os

# 1. Aseguramos que Python encuentre la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.views.session_manager_view import SessionManagerView
from src.ui.components.password_dialog import PasswordDialog
from src.config import THEME
from src.core.utils import get_resource_path

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "Sandbox: Session Manager"
    page.window_width = 1100
    page.window_height = 750
    page.bgcolor = THEME.colors.bg
    page.padding = 0

    # --- DEFINICIÓN DE CALLBACKS (Lógica Simulada) ---
    dummy_files = [
        {
            "icon": ft.Icons.DESKTOP_WINDOWS,
            "title": "Finanzas_2025.json",
            "path": "C:/Usuarios/Admin/Docs/Finanzas_2025.json",
            "last_seen": "Hoy, 10:30"
        },
        {
            "icon": ft.Icons.CLOUD_QUEUE,
            "title": "Backup.json",
            "path": "Google Drive / Mi unidad",
            "last_seen": "Ayer, 18:00"
        }
    ]
    
    def on_dialog_cancel():
        """Cierra el diálogo sin hacer nada."""
        print("Operación cancelada por el usuario.")
        page.close(page.dialog)

    def on_dialog_unlock(password):
        """Simula el intento de desbloqueo de la bóveda."""
        print(f"Intentando desbloquear con la contraseña: '{password}'")
        # Aquí iría la lógica de CryptoManager.decrypt()
        page.close(page.dialog)

    def handle_file_selected(file_name):
        """Se ejecuta cuando el usuario hace clic en una bóveda reciente o local."""
        print(f"Bóveda seleccionada: {file_name}")
        
        # Instanciamos el Dialog pasando el nombre del archivo y los callbacks
        dialog = PasswordDialog(
            file_name=file_name,
            on_unlock=on_dialog_unlock,
            on_cancel=on_dialog_cancel
        )
        
        # Asignamos el diálogo a la página y lo abrimos
        page.dialog = dialog
        page.open(dialog)

    def handle_create_new(e):
        """Se ejecuta al hacer clic en 'Nuevo Archivo'."""
        print("Iniciando el flujo para crear una nueva bóveda...")
        # En la app real, esto navegaría a la vista de creación de bóveda
    
    def handle_load_local(e):
        print("Botón 'Examinar PC' presionado")
        # Aquí iría tu lógica, ej: file_picker.pick_files()

    def handle_load_drive(e):
        print("Botón 'Google Drive' presionado")
        # Aquí iría tu lógica de autenticación OAuth

    def handle_settings(e):
        print("Botón 'Preferencias' presionado")
        # Aquí iría tu lógica para abrir el panel de configuración

    # --- INSTANCIAR LA VISTA (CORREGIDO) ---

    session_view = SessionManagerView(
        page=page,
        recent_files=dummy_files,
        on_load_local=handle_load_local,
        on_load_drive=handle_load_drive,
        on_create_new=handle_create_new,
        on_settings=handle_settings,
        on_file_selected=handle_file_selected
    )
    
    page.add(*session_view.controls)
    page.update()

if __name__ == "__main__":
    # 2. Ruta de assets (para que carguen las fuentes o imágenes si las hay)
    
    assets_path = get_resource_path("assets")
    
    # Ejecutar la app
    ft.app(target=main, assets_dir=assets_path)
    
    
    