import customtkinter as ctk
from src.ui.theme import load_icon
import src.ui.theme as theme

class DriveSelectView(ctk.CTkFrame):
    """
    Shown after a successful Drive auth.
    Lists all .data vaults found in the CryptoVault/ Drive folder
    and lets the user pick one to download and open.
    """

    def __init__(self, master, controller, vaults: list):
        super().__init__(master)
        self.controller = controller
        self.vaults     = vaults   # list of {id, name, modifiedTime, ...}

        # ── Back bar ──────────────────────────────────────────────────────
        back_bar = ctk.CTkFrame(self, fg_color="transparent")
        back_bar.pack(fill="x", padx=12, pady=(12, 0))

        self._icon_arrow = load_icon("back_arrow.png", size=(16,16))
        self._icon_drive = load_icon("sync_green.png", size=(20,20))
        ctk.CTkButton(
            back_bar, text="Volver",
            image=self._icon_arrow,
            compound="left",
            width=90, height=28,
            fg_color="transparent", border_width=1,
            border_color="#555555", text_color=theme.c("text_secondary"),
            hover_color=theme.c("hover"),
            command=self.controller.app.show_welcome_view
        ).pack(side="left")

        # ── Title ─────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Bóvedas en Google Drive",
            image=self._icon_drive,
            compound="left",
            font=theme.font(20, "bold")
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Selecciona la bóveda que deseas abrir.",
            font=theme.font(13), text_color="#888888"
        ).pack(pady=(0, 16))

        # ── Vault list ────────────────────────────────────────────────────
        list_frame = ctk.CTkScrollableFrame(self, label_text="")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        for vault in vaults:
            self._build_vault_row(list_frame, vault)

        # ── Status label ──────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", font=theme.font(12))
        self.status_label.pack(pady=(0, 12))

    # ── helpers ───────────────────────────────────────────────────────────

    def _build_vault_row(self, parent, vault: dict):
        row = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=8)
        row.pack(fill="x", pady=4, padx=4)

        # File name
        name = vault.get("name", "vault.data")
        modified = vault.get("modifiedTime", "")
        if modified:
            # ISO8601 → show only date part
            modified = modified[:10]

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        ctk.CTkLabel(
            info_frame, text=name,
            font=theme.font(14, "bold"), anchor="w"
        ).pack(anchor="w")

        if modified:
            ctk.CTkLabel(
                info_frame, text=f"Modificado: {modified}",
                font=theme.font(11), text_color="#666666", anchor="w"
            ).pack(anchor="w")

        ctk.CTkButton(
            row, text="Abrir",
            width=80, height=32,
            fg_color=theme.c("accent"), hover_color=theme.c("accent_hover"),
            command=lambda v=vault: self._on_select(v)
        ).pack(side="right", padx=12, pady=10)

    def _on_select(self, vault: dict):
        self.status_label.configure(
            text=f"Descargando {vault['name']}...", text_color="#888888"
        )
        self.update_idletasks()
        self.controller.handle_drive_vault_selected(vault["id"], vault["name"])