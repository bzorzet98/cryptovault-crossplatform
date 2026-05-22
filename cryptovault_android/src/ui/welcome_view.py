import customtkinter as ctk


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
            font=("Roboto", 30, "bold")
        ).pack(pady=(50, 4))

        ctk.CTkLabel(
            self,
            text="Tu gestor de contraseñas cifrado",
            font=("Roboto", 13), text_color="#888888"
        ).pack(pady=(0, 40))

        ctk.CTkLabel(
            self, text="¿Cómo deseas ingresar?",
            font=("Roboto", 14)
        ).pack(pady=(0, 16))

        # ── Buttons ───────────────────────────────────────────────────────
        self.btn_local = ctk.CTkButton(
            self,
            text="📂  Abrir Bóveda Local",
            height=44,
            fg_color="transparent", border_width=2,
            command=controller.handle_load_file
        )
        self.btn_local.pack(pady=8, padx=50, fill="x")

        self.btn_drive = ctk.CTkButton(
            self,
            text="☁  Cargar desde Google Drive",
            height=44,
            fg_color="#2c8558", hover_color="#1e5c3d",
            command=controller.handle_drive_connection
        )
        self.btn_drive.pack(pady=8, padx=50, fill="x")

        # Separator
        ctk.CTkLabel(
            self, text="─────  o  ─────",
            font=("Roboto", 11), text_color="#444444"
        ).pack(pady=(12, 4))

        self.btn_new = ctk.CTkButton(
            self,
            text="✦  Crear Nueva Bóveda",
            height=40,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color="#aaaaaa",
            hover_color="#2a2a2a",
            command=controller.handle_create_vault
        )
        self.btn_new.pack(pady=4, padx=50, fill="x")

        # ── Status / loading label ─────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", font=("Roboto", 12))
        self.status_label.pack(pady=16)

    # ── Standard interface ────────────────────────────────────────────────

    def show_message(self, text: str, msg_type: str = "info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
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