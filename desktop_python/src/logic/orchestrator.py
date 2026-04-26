import os
import sys
import time
from src.core.crypto import CryptoManager
from src.core.storage import StorageManager
from src.core.drive_manager import DriveManager


class VaultOrchestrator:
    """
    Central brain of CryptoVault.

    State flags:
        drive_source  — True if the current vault was loaded from / is linked to Drive.
        read_only     — Edits disabled; toggled from dashboard.
        master_key    — None when no session is open.
        mode          — "SYNC" | "NORMAL"  (mirrors drive_source for legacy view reads).
    """

    def __init__(self, app_root):
        self.app = app_root
        self.crypto  = CryptoManager()
        self.master_key = None

        self.drive_source = False
        self.read_only    = False
        self._last_decrypted_data = None
        self._exit_then_quit      = False

        # ── Environment detection ──────────────────────────────────────────
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # logic → src → desktop_python
            self.base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        # ── Paths ──────────────────────────────────────────────────────────
        self.vault_path = os.path.join(self.base_dir, 'vault.data')
        self.cred_path  = os.path.join(self.base_dir, 'credentials.json')
        self.token_path = os.path.join(self.base_dir, 'token.json')

        # ── Managers ───────────────────────────────────────────────────────
        self.drive   = DriveManager(credentials_path=self.cred_path,
                                    token_path=self.token_path)
        self.storage = StorageManager(file_path=self.vault_path)
        self.mode    = "NORMAL"

    # ══════════════════════════════════════════════════════════════════════
    # STARTUP
    # ══════════════════════════════════════════════════════════════════════

    def start_app(self):
        self.app.show_welcome_view()

    # ══════════════════════════════════════════════════════════════════════
    # WELCOME ─ open local file
    # ══════════════════════════════════════════════════════════════════════

    def handle_load_file(self):
        """Native file-picker → pick any .data from disk → Login."""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            title="Seleccionar bóveda",
            initialdir=self.base_dir,
            filetypes=[("Bóvedas CryptoVault", "*.data"), ("Todos los archivos", "*.*")]
        )
        if not filepath:
            return

        self.storage      = StorageManager(file_path=filepath)
        self.vault_path   = filepath
        self.drive_source = False
        self._sync_mode()
        self.app.show_login_view()

    def handle_create_vault(self):
        """
        Let the user choose a name and location for the new vault,
        then go to Setup to set the master password.
        """
        from tkinter import filedialog

        dest = filedialog.asksaveasfilename(
            title="Crear nueva bóveda",
            initialdir=self.base_dir,
            initialfile="mi_boveda.data",
            defaultextension=".data",
            filetypes=[("Bóveda CryptoVault", "*.data"), ("Todos los archivos", "*.*")]
        )
        if not dest:
            return  # user cancelled

        self.storage      = StorageManager(file_path=dest)
        self.vault_path   = dest
        self.drive_source = False
        self._sync_mode()
        self.app.show_setup_view()

    # ══════════════════════════════════════════════════════════════════════
    # WELCOME ─ open from Drive
    # ══════════════════════════════════════════════════════════════════════

    def handle_drive_connection(self):
        """
        Authenticates with Google Drive and lists available vaults.
        Shows a picker if files exist; offers Setup if none found.
        """
        self.app.show_loading_view()
        loading = self.app.current_view
        loading.update_status("Conectando con Google...", 0.3)
        self.app.update_idletasks()

        try:
            loading.update_status("Autenticando...", 0.5)
            self.drive.authenticate()
            loading.update_status("Buscando bóvedas en Drive...", 0.8)
            vaults = self.drive.list_vaults()
            loading.update_status("Listo.", 1.0)
            self.app.update_idletasks()

        except Exception as e:
            self.app.show_welcome_view()
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(f"Error de conexión: {e}", "error")
            return

        if not vaults:
            # No vaults in Drive — offer to create one that will auto-sync
            self.drive_source = True
            self._sync_mode()
            self.app.show_setup_view()
        else:
            self.app.show_drive_select_view(vaults)

    def handle_drive_vault_selected(self, file_id: str, filename: str):
        """
        Called by DriveSelectView when user picks a vault.
        Downloads it locally and goes to Login.
        """
        self.app.show_loading_view()
        loading = self.app.current_view
        loading.update_status(f"Descargando {filename}...", 0.5)
        self.app.update_idletasks()

        try:
            local_path = os.path.join(self.base_dir, filename)
            self.drive.download_vault(file_id, local_path)

            self.storage      = StorageManager(file_path=local_path)
            self.vault_path   = local_path
            self.drive_source = True
            self._sync_mode()

            loading.update_status("¡Descarga completa!", 1.0)
            self.app.update_idletasks()
            self.app.after(500, self.app.show_login_view)

        except Exception as e:
            self.app.show_welcome_view()
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(f"Error al descargar: {e}", "error")

    # ══════════════════════════════════════════════════════════════════════
    # LOGIN / SETUP
    # ══════════════════════════════════════════════════════════════════════

    def handle_login(self, password):
        try:
            encrypted_data = self.storage.load_vault()
            vault_dict     = self.crypto.decrypt(encrypted_data, password)
            self.master_key             = password
            self._last_decrypted_data   = vault_dict
            self.app.show_dashboard_view(vault_dict)
        except Exception:
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message("Contraseña incorrecta", "error")

    def handle_setup(self, password):
        """Creates empty vault, saves it, and optionally syncs to Drive."""
        initial_data    = {"items": []}
        encrypted       = self.crypto.encrypt(initial_data, password)
        self.storage.save_vault(encrypted)
        self.master_key           = password
        self._last_decrypted_data = initial_data

        if self.drive_source:
            # Auto-upload the new vault so it lives in Drive from the start
            self._do_sync_upload()
        else:
            self.app.show_dashboard_view(initial_data)

    # ══════════════════════════════════════════════════════════════════════
    # DASHBOARD ─ add credential
    # ══════════════════════════════════════════════════════════════════════

    def handle_save_credential(self, name, username, password):
        """Saves credential locally. Sync happens on exit or manually."""
        try:
            encrypted  = self.storage.load_vault()
            vault_dict = self.crypto.decrypt(encrypted, self.master_key)
            vault_dict['items'].append(
                {"name": name, "username": username, "password": password}
            )
            self.storage.save_vault(self.crypto.encrypt(vault_dict, self.master_key))
            self._last_decrypted_data = vault_dict

            if hasattr(self.app.current_view, 'render'):
                self.app.current_view.render(vault_dict)
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message("Credencial guardada.", "success")

        except Exception as e:
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(f"Error al guardar: {e}", "error")

    # ══════════════════════════════════════════════════════════════════════
    # DASHBOARD ─ sync to Drive  (manual button, only visible when LOCAL)
    # ══════════════════════════════════════════════════════════════════════

    def handle_sync_drive(self, then_quit=False):
        """
        Uploads current vault to Drive.
        If then_quit=True, closes the app afterwards.
        """
        self.app.show_loading_view()
        loading = self.app.current_view
        loading.update_status("Conectando con Drive...", 0.2)
        self.app.update_idletasks()

        try:
            if not self.drive.is_authenticated():
                self.drive.authenticate()

            loading.update_status("Subiendo archivo...", 0.6)
            self.app.update_idletasks()
            self.drive.upload_vault(self.storage.get_path())

            self.drive_source = True
            self._sync_mode()
            loading.update_status("¡Sincronización exitosa!", 1.0)
            self.app.update_idletasks()
            time.sleep(0.5)

            if then_quit:
                self._finish_exit(then_quit=True)
            else:
                self.app.show_dashboard_view(self._last_decrypted_data)
                if hasattr(self.app.current_view, 'show_message'):
                    self.app.current_view.show_message(
                        "Bóveda sincronizada con Drive ☁", "success"
                    )

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error de sincronización", str(e))
            if then_quit:
                self._finish_exit(then_quit=True)
            else:
                self.app.show_dashboard_view(self._last_decrypted_data)

    # ══════════════════════════════════════════════════════════════════════
    # DASHBOARD ─ export vault
    # ══════════════════════════════════════════════════════════════════════

    def handle_export_vault(self):
        """
        Saves a copy of the current vault to a user-chosen location/name.
        Works regardless of drive_source.
        """
        from tkinter import filedialog
        import shutil

        current_name = os.path.basename(self.storage.get_path())
        dest = filedialog.asksaveasfilename(
            title="Exportar bóveda como...",
            initialdir=os.path.expanduser("~"),
            initialfile=current_name,
            defaultextension=".data",
            filetypes=[("Bóveda CryptoVault", "*.data"), ("Todos los archivos", "*.*")]
        )
        if not dest:
            return

        try:
            shutil.copy2(self.storage.get_path(), dest)
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(
                    f"Exportado: {os.path.basename(dest)}", "success"
                )
        except Exception as e:
            if hasattr(self.app.current_view, 'show_message'):
                self.app.current_view.show_message(f"Error al exportar: {e}", "error")

    # ══════════════════════════════════════════════════════════════════════
    # EXIT FLOW
    # ══════════════════════════════════════════════════════════════════════

    def handle_exit(self, then_quit=False):
        """
        ← Menú  (then_quit=False) → cleans session and goes straight to WelcomeView.
        🔒 Cerrar (then_quit=True)  → goes through ExitView to offer Drive sync before quit.
        """
        self._exit_then_quit = then_quit

        if then_quit:
            if self.master_key:
                self.app.show_exit_view(mode="QUIT")
            else:
                self._finish_exit(then_quit=True)
        else:
            # Back to menu: reset session and go directly, no confirmation
            self._finish_exit(then_quit=False)

    def handle_exit_sync_and_finish(self, then_quit: bool):
        """Called by ExitView 'Sincronizar y salir'."""
        self.handle_sync_drive(then_quit=then_quit)

    def handle_save_local_and_finish(self, then_quit: bool):
        """Called by ExitView 'Guardar local y salir'. Data is already saved."""
        self._finish_exit(then_quit)

    def handle_cancel_exit(self):
        """User pressed Cancelar on ExitView — go back to dashboard."""
        self.app.show_dashboard_view(self._last_decrypted_data)

    def _finish_exit(self, then_quit: bool):
        """
        Resets session state and navigates to menu or closes app.
        Always wipes token.json so Drive requires fresh auth next time
        (lazy / stateless auth strategy).
        """
        self.master_key           = None
        self.read_only            = False
        self.drive_source         = False
        self._last_decrypted_data = None
        self._sync_mode()

        # ── Lazy auth: delete token so next Drive action re-authenticates ──
        self._wipe_drive_session()

        if then_quit:
            self.app.destroy()
        else:
            self.app.show_welcome_view()

    def _wipe_drive_session(self):
        """Removes token.json and clears the in-memory Drive service."""
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
        except Exception as e:
            print(f"Could not remove token.json: {e}")
        self.drive.service = None  # is_authenticated() will return False

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _sync_mode(self):
        """Keep self.mode aligned with drive_source (legacy compatibility)."""
        self.mode = "SYNC" if self.drive_source else "NORMAL"

    def _do_sync_upload(self):
        """Internal helper: upload without showing a separate loading screen."""
        try:
            if not self.drive.is_authenticated():
                self.drive.authenticate()
            self.drive.upload_vault(self.storage.get_path())
            self.drive_source = True
            self._sync_mode()
        except Exception as e:
            print(f"Auto-sync failed: {e}")
        finally:
            self.app.show_dashboard_view(self._last_decrypted_data)