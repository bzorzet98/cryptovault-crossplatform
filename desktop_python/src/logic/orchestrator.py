import os
import sys
import time
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
            # Si es ejecutable, la raíz es donde está el .exe
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # CORRECCIÓN: Si es script, subimos exactamente 3 niveles.
            # orchestrator.py (1) -> logic (2) -> src (3) -> desktop_python
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        """Secuencia de arranque: Sincroniza en segundo plano y termina SIEMPRE en Bienvenida."""
        self.app.show_loading_view()
        loading_screen = self.app.current_view

        try:
            loading_screen.update_status("Buscando configuraciones...", 0.2)
            
            # 1. Determinar el modo inicial según el token
            if os.path.exists(self.token_path):
                self.mode = "SYNC"
                loading_screen.update_status("Sincronizando con Drive...", 0.5)
                
                # Sincronización silenciosa: intentamos bajar la última versión
                try:
                    self.drive.authenticate() 
                    file_id = self.drive.find_file("vault.data")
                    if file_id:
                        self.drive.download_file(file_id, self.vault_path)
                        loading_screen.update_status("Nube actualizada.", 0.8)
                except Exception as e:
                    # Si falla el internet, no pasa nada, seguimos con lo que hay local
                    print(f"Modo Offline: {e}")
            else:
                self.mode = "NORMAL"
                loading_screen.update_status("Modo local.", 0.6)

            # 2. FINALIZACIÓN: Siempre vamos a WelcomeView, pase lo que pase
            # Le damos 1 segundo para que el usuario vea que terminó de cargar
            self.app.after(1000, self.app.show_welcome_view)

        except Exception as e:
            print(f"Error crítico en arranque: {e}")
            # En caso de error total, también volvemos a la bienvenida por seguridad
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
            if hasattr(self.app.current_view, 'toggle_loading'):
                self.app.current_view.toggle_loading(False)

    def handle_drive_logout(self):
        """Elimina el vínculo con Google Drive de forma silenciosa."""
        import os
        try:
            # 1. Borramos el archivo físico del token
            if os.path.exists(self.token_path):
                try:
                    os.remove(self.token_path)
                    print("Token eliminado físicamente.")
                except Exception as e:
                    print(f"Error al eliminar token: {e}")
                
            # 2. Cambiamos el modo de la app ANTES de cualquier otra cosa
            self.mode = "NORMAL"
            
            # 3. IMPORTANTE: No re-instanciamos DriveManager aquí para evitar que abra el navegador.
            if self.drive:
                self.drive.service = None 

            if hasattr(self.app.current_view, 'vault_data'):
                current_data = self.app.current_view.vault_data
                self.app.show_dashboard_view(current_data)
                
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message("Se ha desvinculado de Google Drive.", "info")
                    
        except Exception as e:
            print(f"Error al desvincular: {e}")
            
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
        """Cierra la sesión y vuelve SIEMPRE a la pantalla de bienvenida."""
        self.master_key = None
        self.mode = "NORMAL" # Resetear modo por seguridad
        self.app.show_welcome_view()


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
        """Sube la bóveda a Google Drive y actualiza la interfaz al modo SYNC."""
        if hasattr(self.app.current_view, 'toggle_loading'):
            self.app.current_view.toggle_loading(True)
            
        try:
            local_vault_path = self.storage.get_path()
            
            # 1. Subir a Drive
            self.drive.upload_vault(local_vault_path)
            
            # 2. Actualizar el estado interno de la app a modo nube
            self.mode = "SYNC"
            
            # 3. Recargar el Dashboard para que aparezca el botón "Desvincular"
            # Volvemos a leer y desencriptar los datos para pasárselos a la vista fresca
            encrypted_data = self.storage.load_vault()
            vault_dict = self.crypto.decrypt(encrypted_data, self.master_key)
            self.app.show_dashboard_view(vault_dict)
            
            # 4. Mostrar el mensaje en la nueva vista generada
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message("Sincronizado y vinculado a Drive correctamente.", "success")
                
        except Exception as e:
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(f"Error de sincronización: {e}", "error")
        finally:
            if hasattr(self.app.current_view, 'toggle_loading'):
                self.app.current_view.toggle_loading(False)