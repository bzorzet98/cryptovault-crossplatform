import os
import threading
from kivy.clock import Clock
from src.core.crypto import CryptoManager
from src.core.storage import StorageManager
from src.core.drive_manager import DriveManager
from src.core.vault_schema import (
    build_default_vault, new_credential, new_user_tab,
    purge_old_deleted, get_tab, now_iso, DELETED_TAB_ID
)


def _get_base_dir():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except ImportError:
        # Running on Linux desktop during development
        return os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )


class VaultOrchestrator:
    """
    Central brain of CryptoVault Android.
    Same logic as desktop — Clock replaces app.after(), paths adapted for Android.
    """

    def __init__(self, app):
        self.app        = app
        self.crypto     = CryptoManager()
        self.master_key = None

        self.drive_source = False
        self.read_only    = False
        self._last_decrypted_data = None

        self.base_dir   = _get_base_dir()
        self.vault_path = os.path.join(self.base_dir, 'vault.data')
        self.cred_path  = os.path.join(self.base_dir, 'credentials.json')
        self.token_path = os.path.join(self.base_dir, 'token.json')

        self.drive   = DriveManager(credentials_path=self.cred_path,
                                    token_path=self.token_path)
        self.storage = StorageManager(file_path=self.vault_path)
        self.mode    = "NORMAL"

        self._auto_lock_after = 120   # seconds
        self._auto_lock_event = None
        self._clipboard_event = None

    # ══════════════════════════════════════════════════════════════════════
    # AUTO-LOCK
    # ══════════════════════════════════════════════════════════════════════

    def reset_auto_lock(self):
        if self._auto_lock_event:
            self._auto_lock_event.cancel()
        if self.master_key:
            self._auto_lock_event = Clock.schedule_once(
                self._do_auto_lock, self._auto_lock_after
            )

    def _do_auto_lock(self, dt):
        if self.master_key:
            self._finish_exit(then_quit=False)

    # ══════════════════════════════════════════════════════════════════════
    # CLIPBOARD CLEAR
    # ══════════════════════════════════════════════════════════════════════

    def schedule_clipboard_clear(self, delay=30):
        if self._clipboard_event:
            self._clipboard_event.cancel()
        self._clipboard_event = Clock.schedule_once(
            self._do_clear_clipboard, delay
        )

    def _do_clear_clipboard(self, dt):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy("")
        except Exception:
            pass
        self._clipboard_event = None

    # ══════════════════════════════════════════════════════════════════════
    # STARTUP
    # ══════════════════════════════════════════════════════════════════════

    def start_app(self):
        self.app.show_welcome_screen()

    # ══════════════════════════════════════════════════════════════════════
    # WELCOME — open local file
    # ══════════════════════════════════════════════════════════════════════

    def handle_load_file(self, filepath):
        """Receives filepath from the file picker and goes to Login."""
        self.storage      = StorageManager(file_path=filepath)
        self.vault_path   = filepath
        self.drive_source = False
        self._sync_mode()
        self.app.show_login_screen()

    def handle_create_vault(self, filepath):
        """Creates a new vault at the given path and goes to Setup."""
        self.storage      = StorageManager(file_path=filepath)
        self.vault_path   = filepath
        self.drive_source = False
        self._sync_mode()
        self.app.show_setup_screen()

    # ══════════════════════════════════════════════════════════════════════
    # WELCOME — Google Drive
    # ══════════════════════════════════════════════════════════════════════

    def handle_drive_connection(self):
        """Authenticates with Drive in a background thread to avoid UI freeze."""
        self.app.show_loading_screen("Conectando con Google Drive...")

        def _worker():
            try:
                self.drive.authenticate()
                vaults = self.drive.list_vaults()
                # Always update UI from the main thread
                Clock.schedule_once(lambda dt: self._on_drive_connected(vaults), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_drive_error(str(e)), 0)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_drive_connected(self, vaults):
        if not vaults:
            self.drive_source = True
            self._sync_mode()
            self.app.show_setup_screen()
        else:
            self.app.show_drive_select_screen(vaults)

    def _on_drive_error(self, error):
        self.app.show_welcome_screen()
        self.app.show_toast(f"Error de conexión: {error}")

    def handle_drive_vault_selected(self, file_id, filename):
        self.app.show_loading_screen(f"Descargando {filename}...")

        def _worker():
            try:
                local_path = os.path.join(self.base_dir, filename)
                self.drive.download_vault(file_id, local_path)
                self.storage      = StorageManager(file_path=local_path)
                self.vault_path   = local_path
                self.drive_source = True
                self._sync_mode()
                Clock.schedule_once(lambda dt: self.app.show_login_screen(), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_drive_error(str(e)), 0)

        threading.Thread(target=_worker, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════
    # LOGIN / SETUP
    # ══════════════════════════════════════════════════════════════════════

    def handle_login(self, password):
        try:
            encrypted_data            = self.storage.load_vault()
            vault_dict                = self.crypto.decrypt(encrypted_data, password)
            self.master_key           = password
            self._last_decrypted_data = vault_dict
            self.reset_auto_lock()
            self.app.show_dashboard_screen(vault_dict)
        except Exception:
            self.app.show_toast("Contraseña incorrecta")

    def handle_setup(self, password):
        initial_data              = build_default_vault()
        encrypted                 = self.crypto.encrypt(initial_data, password)
        self.storage.save_vault(encrypted)
        self.master_key           = password
        self._last_decrypted_data = initial_data
        self.reset_auto_lock()

        if self.drive_source:
            self._do_sync_upload()
        else:
            self.app.show_dashboard_screen(initial_data)

    # ══════════════════════════════════════════════════════════════════════
    # DASHBOARD — credential & tab handlers
    # ══════════════════════════════════════════════════════════════════════

    def _persist(self, vault_dict):
        self.storage.save_vault(self.crypto.encrypt(vault_dict, self.master_key))
        self._last_decrypted_data = vault_dict

    def handle_add_credential(self, tab_id, name, fields, extra_fields):
        vault = self._last_decrypted_data
        tab   = get_tab(vault, tab_id)
        if not tab:
            return
        tab["credentials"].append(new_credential(name, fields, extra_fields))
        self._persist(vault)

    def handle_update_credential(self, tab_id, updated_credential):
        vault = self._last_decrypted_data
        tab   = get_tab(vault, tab_id)
        if not tab:
            return
        for i, c in enumerate(tab["credentials"]):
            if c["id"] == updated_credential["id"]:
                tab["credentials"][i] = updated_credential
                break
        self._persist(vault)

    def handle_delete_credential(self, tab_id, credential_id):
        vault = self._last_decrypted_data
        tab   = get_tab(vault, tab_id)
        if not tab:
            return
        cred = next((c for c in tab["credentials"] if c["id"] == credential_id), None)
        if not cred:
            return
        tab["credentials"]  = [c for c in tab["credentials"] if c["id"] != credential_id]
        cred["deleted_at"]  = now_iso()
        deleted_tab = get_tab(vault, DELETED_TAB_ID)
        if deleted_tab:
            deleted_tab["credentials"].append(cred)
        self._persist(vault)

    def handle_restore_credential(self, credential_id, target_tab_id):
        vault       = self._last_decrypted_data
        deleted_tab = get_tab(vault, DELETED_TAB_ID)
        if not deleted_tab:
            return
        cred = next((c for c in deleted_tab["credentials"] if c["id"] == credential_id), None)
        if not cred:
            return
        deleted_tab["credentials"] = [
            c for c in deleted_tab["credentials"] if c["id"] != credential_id
        ]
        cred["deleted_at"] = None
        target = get_tab(vault, target_tab_id)
        if target:
            target["credentials"].append(cred)
        self._persist(vault)

    def handle_add_tab(self, name, icon, default_fields):
        vault = self._last_decrypted_data
        new_tab = new_user_tab(name, icon, default_fields)
        deleted_idx = next(
            (i for i, t in enumerate(vault["tabs"]) if t["id"] == DELETED_TAB_ID),
            len(vault["tabs"])
        )
        vault["tabs"].insert(deleted_idx, new_tab)
        self._persist(vault)
        return new_tab

    def handle_delete_tab(self, tab_id):
        vault = self._last_decrypted_data
        tab   = get_tab(vault, tab_id)
        if not tab or tab.get("is_system"):
            return False
        for cred in tab["credentials"]:
            cred["deleted_at"] = now_iso()
        deleted_tab = get_tab(vault, DELETED_TAB_ID)
        if deleted_tab:
            deleted_tab["credentials"].extend(tab["credentials"])
        vault["tabs"] = [t for t in vault["tabs"] if t["id"] != tab_id]
        self._persist(vault)
        return True

    # ══════════════════════════════════════════════════════════════════════
    # SYNC TO DRIVE
    # ══════════════════════════════════════════════════════════════════════

    def handle_sync_drive(self):
        self.app.show_loading_screen("Sincronizando con Drive...")

        def _worker():
            try:
                if not self.drive.is_authenticated():
                    self.drive.authenticate()
                self.drive.upload_vault(self.storage.get_path())
                self.drive_source = True
                self._sync_mode()
                Clock.schedule_once(lambda dt: self._on_sync_done(), 0)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.app.show_toast(f"Error: {e}"), 0
                )
                Clock.schedule_once(
                    lambda dt: self.app.show_dashboard_screen(self._last_decrypted_data), 0
                )

        threading.Thread(target=_worker, daemon=True).start()

    def _on_sync_done(self):
        self.app.show_dashboard_screen(self._last_decrypted_data)
        self.app.show_toast("Bóveda sincronizada con Drive ☁")

    def _do_sync_upload(self):
        def _worker():
            try:
                if not self.drive.is_authenticated():
                    self.drive.authenticate()
                self.drive.upload_vault(self.storage.get_path())
                self.drive_source = True
                self._sync_mode()
            except Exception as e:
                print(f"Auto-sync failed: {e}")
            finally:
                Clock.schedule_once(
                    lambda dt: self.app.show_dashboard_screen(self._last_decrypted_data), 0
                )

        threading.Thread(target=_worker, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════
    # EXIT
    # ══════════════════════════════════════════════════════════════════════

    def handle_exit(self):
        """Wipes session and returns to welcome screen."""
        self._finish_exit(then_quit=False)

    def _finish_exit(self, then_quit):
        self.master_key           = None
        self.read_only            = False
        self.drive_source         = False
        self._last_decrypted_data = None
        self._sync_mode()
        self._wipe_drive_session()

        if self._auto_lock_event:
            self._auto_lock_event.cancel()

        if then_quit:
            self.app.stop()
        else:
            self.app.show_welcome_screen()

    def _wipe_drive_session(self):
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
        except Exception as e:
            print(f"Could not remove token.json: {e}")
        self.drive.service = None

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _sync_mode(self):
        self.mode = "SYNC" if self.drive_source else "NORMAL"