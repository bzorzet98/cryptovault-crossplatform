import customtkinter as ctk
from desktop.ui.themes.theme import load_icon
import desktop.ui.themes.theme as theme
from desktop.ui.dialogs.settings_dialog  import SettingsDialog

class WelcomeView(ctk.CTkFrame):
    """
    Entry screen.

    Two actions:
        📂 Abrir Bóveda Local  → native file-picker for any .data file
        ☁  Cargar desde Google Drive → auth + list vaults in Drive
    """

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # ── Branding ──────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="CryptoVault",
            font=theme.font(30, "bold")
        ).pack(pady=(50, 4))

        ctk.CTkLabel(
            self,
            text="Tu gestor de contraseñas cifrado",
            font=theme.font(13), text_color="#888888"
        ).pack(pady=(0, 40))

        ctk.CTkLabel(
            self, text="¿Cómo deseas ingresar?",
            font=theme.font(14)
        ).pack(pady=(0, 16))

        # ── Buttons ───────────────────────────────────────────────────────
        _icon_lock = load_icon("lock_icon.png")
        self.btn_local = ctk.CTkButton(
            self,
            text="Abrir Bóveda Local",
            image=_icon_lock,
            compound="left",
            height=44,
            fg_color="transparent", border_width=2,
            command=controller.handle_load_file
        )
        self.btn_local.pack(pady=8, padx=50, fill="x")

        _icon_sync = load_icon("sync_white.png")
        self.btn_drive = ctk.CTkButton(
            self,
            text="Cargar desde Google Drive",
            image=_icon_sync,
            compound="left",
            height=44,
            fg_color=theme.c("accent"), hover_color=theme.c("accent_hover"),
            command=controller.handle_drive_connection
        )
        self.btn_drive.pack(pady=8, padx=50, fill="x")

        # Separator
        ctk.CTkLabel(
            self, text="─────  o  ─────",
            font=theme.font(11), text_color="#444444"
        ).pack(pady=(12, 4))
        
        _icon_files = load_icon("copy_white.png", size=(16,16))
        self.btn_new = ctk.CTkButton(
            self,
            text="Crear Nueva Bóveda",
            image=_icon_files,
            compound="left",
            height=40,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=theme.c("text_secondary"),
            hover_color="#2a2a2a",
            command=controller.handle_create_vault
        )
        self.btn_new.pack(pady=4, padx=50, fill="x")

        # ── Status / loading label ─────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", font=theme.font(12))
        self.status_label.pack(pady=16)
        
        ctk.CTkButton(
                self,
                text="Preferencias",
                width=140,
                command=self._show_settings
            ).pack(pady=(10, 0))

    # ── Standard interface ────────────────────────────────────────────────

    def show_message(self, text: str, msg_type: str = "info"):
        color = "#ff4d4d" if msg_type == "error" else theme.c("accent")
        self.status_label.configure(text=text, text_color=color)

    def toggle_loading(self, is_loading: bool):
        state = "disabled" if is_loading else "normal"
        self.btn_local.configure(state=state)
        self.btn_drive.configure(state=state)
        self.btn_new.configure(state=state)
        self.status_label.configure(
            text="Conectando... por favor espera." if is_loading else "",
            text_color="#888888"
        )
        
    def _show_settings(self):
        SettingsDialog(
            self,
            on_apply=self._reload_ui
        )
    
    def _reload_ui(self):
        self.controller.app.show_welcome_view()