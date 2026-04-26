import customtkinter as ctk


class ExitView(ctk.CTkFrame):
    """
    Exit / logout confirmation screen.

    mode="QUIT"   → user wants to close the app entirely.
                    If local: offer Sync+Quit or Just Quit.
                    If synced: show "Syncing..." and quit.

    mode="LOGOUT" → user wants to go back to the Welcome menu.
                    If local: offer to save a Drive copy or just go to menu.
                    If synced: auto-sync (show loading) then go to menu.
    """

    def __init__(self, master, controller, mode: str = "QUIT"):
        super().__init__(master)
        self.controller = controller
        self.mode       = mode
        is_sync         = getattr(controller, 'drive_source', False)
        then_quit       = (mode == "QUIT")

        # ── Title ─────────────────────────────────────────────────────────
        title = "¿Cerrar CryptoVault?" if then_quit else "¿Volver al menú principal?"
        ctk.CTkLabel(
            self, text=title,
            font=("Roboto", 22, "bold")
        ).pack(pady=(40, 8))

        # ── Subtitle / explanation ─────────────────────────────────────────
        if is_sync:
            subtitle = (
                "La bóveda está vinculada a Google Drive.\n"
                "Se sincronizará automáticamente antes de salir."
            )
        else:
            subtitle = (
                "La bóveda está guardada localmente.\n"
                "¿Deseas subir una copia a Google Drive antes de salir?"
            )

        ctk.CTkLabel(
            self, text=subtitle,
            font=("Roboto", 13), text_color="#888888",
            justify="center"
        ).pack(pady=(0, 30))

        # ── Buttons ────────────────────────────────────────────────────────
        btn_w = 260

        if is_sync:
            # Already in Drive — single primary action
            ctk.CTkButton(
                self,
                text="☁ Sincronizar y salir" if then_quit else "☁ Sincronizar y volver al menú",
                width=btn_w, height=40,
                fg_color="#2c8558", hover_color="#1e5c3d",
                command=lambda: controller.handle_exit_sync_and_finish(then_quit)
            ).pack(pady=8)

        else:
            # Local vault — offer Drive upload or skip
            ctk.CTkButton(
                self,
                text="☁ Subir a Drive y salir" if then_quit else "☁ Subir a Drive y volver al menú",
                width=btn_w, height=40,
                fg_color="#2c8558", hover_color="#1e5c3d",
                command=lambda: controller.handle_exit_sync_and_finish(then_quit)
            ).pack(pady=8)

            skip_label = "Cerrar sin subir a Drive" if then_quit else "Volver al menú sin subir"
            ctk.CTkButton(
                self,
                text=skip_label,
                width=btn_w, height=40,
                fg_color="#3a3a3a", hover_color="#4a4a4a",
                command=lambda: controller.handle_save_local_and_finish(then_quit)
            ).pack(pady=4)

        # ── Cancel ────────────────────────────────────────────────────────
        ctk.CTkButton(
            self, text="← Cancelar",
            width=btn_w, height=36,
            fg_color="transparent", border_width=1,
            border_color="#555555", text_color="#aaaaaa",
            hover_color="#333333",
            command=controller.handle_cancel_exit
        ).pack(pady=(16, 8))