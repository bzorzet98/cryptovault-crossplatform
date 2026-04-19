import os
import sys
from src.core.crypto import CryptoManager
from src.core.storage import StorageManager
from src.core.drive_manager import DriveManager

class VaultOrchestrator:
    def __init__(self, app_root):
        self.app = app_root
        self.crypto = CryptoManager()
        self.master_key = None
        
        # --- DETECCIÓN DE ENTORNO (EXE vs VS Code) ---
        if getattr(sys, 'frozen', False):
            # Si estamos corriendo como un ejecutable compilado (.exe / binario)
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # Si estamos corriendo como script de Python normal
            # Subimos 3 niveles desde src/logic/orchestrator.py hasta la raíz y apuntamos a desktop_python
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.base_dir = os.path.join(root_dir, 'desktop_python')

        # --- RUTAS ABSOLUTAS DEFINITIVAS ---
        self.vault_path = os.path.join(self.base_dir, 'vault.data')
        self.cred_path = os.path.join(self.base_dir, 'credentials.json')
        self.token_path = os.path.join(self.base_dir, 'token.json')

        # Instanciamos los managers inyectándoles las rutas correctas
        self.drive = DriveManager(credentials_path=self.cred_path, token_path=self.token_path)
        
        # Le decimos al StorageManager exactamente dónde guardar
        self.storage = StorageManager(file_path=self.vault_path)

        self.mode = "NORMAL"  # MODOS: NORMAL, SYNC, READ_ONLY
    # --- CICLO DE VIDA Y NAVEGACIÓN ---

    def start_app(self):
        """Decide el punto de entrada basado en la existencia de datos."""
        if self.storage.vault_exists():
            # Si hay datos locales, vamos a login directo
            self.app.show_login_view()
        else:
            # Si no hay nada, preguntamos qué quiere hacer el usuario
            self.app.show_welcome_view()

    def handle_drive_connection(self):
        """Conecta a Drive e intenta recuperar datos."""
        self.app.current_view.toggle_loading(True)
        try:
            self.drive.authenticate()
            file_id = self.drive.find_file("vault.data")
            
            if file_id:
                self.drive.download_file(file_id, self.storage.get_path())
                self.mode = "SYNC" # Activamos modo sincronizado
                self.app.show_login_view()
            else:
                # No hay archivo, pero activamos SYNC para que la nueva se suba
                self.mode = "SYNC"
                self.app.show_setup_view()
        except Exception as e:
            self.app.current_view.show_message(f"Error Drive: {e}", "error")
        finally:
            self.app.current_view.toggle_loading(False)

    def handle_readonly_setup(self):
        """Activa el modo donde puedes ver pero no tocar."""
        self.mode = "READ_ONLY"
        if self.storage.vault_exists():
            self.app.show_login_view()
        else:
            self.app.current_view.show_message("No hay bóveda local para leer.", "error")
            
    def handle_setup(self, new_password):
        """Crea la bóveda inicial vacía cuando no existe."""
        try:
            self.master_key = new_password
            empty_vault = {"user_id": "local_user", "items": []}
            
            # Encriptar y guardar
            encrypted_data = self.crypto.encrypt(empty_vault, self.master_key)
            self.storage.save_vault(encrypted_data)
            
            # Pasar a la vista principal
            self.app.show_dashboard_view(empty_vault)
        except Exception as e:
            self.app.current_view.show_message(f"Error al crear bóveda: {e}", "error")

    def handle_login(self, password):
        """Intenta abrir la bóveda con la clave proporcionada."""
        try:
            encrypted_data = self.storage.load_vault()
            vault_dict = self.crypto.decrypt(encrypted_data, password)
            
            # Si no falla, la clave es correcta
            self.master_key = password
            self.app.show_dashboard_view(vault_dict)
        except Exception:
            self.app.current_view.show_message("Contraseña incorrecta", "error")

    def handle_logout(self):
        """Limpia la memoria y devuelve al usuario a la pantalla de login."""
        self.master_key = None
        self.app.show_login_view()


    # --- GESTIÓN DE DATOS Y SINCRONIZACIÓN ---

    def handle_save_credential(self, name, username, password):
        """Recibe los datos del formulario UI, actualiza la bóveda y la guarda cifrada."""
        try:
            # 1. Cargar bóveda local actual
            current_data = self.storage.load_vault()
            vault_dict = self.crypto.decrypt(current_data, self.master_key)
            
            # 2. Actualizar lista de items
            new_item = {"name": name, "username": username, "password": password}
            vault_dict['items'].append(new_item)
            
            # 3. Encriptar el nuevo paquete
            encrypted_bundle = self.crypto.encrypt(vault_dict, self.master_key)
            
            # 4. Guardar Localmente
            self.storage.save_vault(encrypted_bundle)
            
            # 5. Refrescar la interfaz
            self.app.current_view.render(vault_dict)
            self.app.current_view.show_message("Credencial guardada correctamente", "success")
            
        except Exception as e:
            self.app.current_view.show_message(f"Error crítico al guardar: {e}", "error")

    def handle_sync_drive(self):
        """Sube la bóveda encriptada local a Google Drive."""
        self.app.current_view.toggle_loading(True)
        try:
            # Se utiliza el método get_path() de storage para evitar problemas de rutas relativas
            local_vault_path = self.storage.get_path()
            
            # Subir a Drive
            self.drive.upload_vault(local_vault_path)
            
            self.app.current_view.show_message("Sincronización exitosa", "success")
        except Exception as e:
            self.app.current_view.show_message(f"Error de sincronización: {e}", "error")
        finally:
            self.app.current_view.toggle_loading(False)