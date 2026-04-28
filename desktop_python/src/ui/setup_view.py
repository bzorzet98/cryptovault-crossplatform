import customtkinter as ctk


class SetupView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller   = controller
        self._pw_visible  = False

        ctk.CTkLabel(
            self, text="Nueva Bóveda",
            font=("Roboto", 24, "bold")
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            self,
            text="Elige una Master Password para cifrar todos tus datos.\nNo podrás recuperarla si la olvidás.",
            font=("Roboto", 13), text_color="#888888", justify="center"
        ).pack(pady=(0, 24))

        # ── Password field ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Master Password *",
                     font=("Roboto", 12), text_color="#aaaaaa").pack(anchor="center")

        pw_row = ctk.CTkFrame(self, fg_color="transparent")
        pw_row.pack(pady=(4, 10))

        self.password_entry = ctk.CTkEntry(
            pw_row, placeholder_text="Mínimo 4 caracteres",
            show="*", width=210, height=36
        )
        self.password_entry.pack(side="left", padx=(0, 6))

        self._toggle_btn = ctk.CTkButton(
            pw_row, text="👁",
            width=36, height=36,
            fg_color="#333333", hover_color="#444444",
            command=self._toggle_visibility
        )
        self._toggle_btn.pack(side="left")

        # ── Confirm field ─────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Confirmar Password *",
                     font=("Roboto", 12), text_color="#aaaaaa").pack(anchor="center")

        conf_row = ctk.CTkFrame(self, fg_color="transparent")
        conf_row.pack(pady=(4, 20))

        self.confirm_entry = ctk.CTkEntry(
            conf_row, placeholder_text="Repetí la misma clave",
            show="*", width=210, height=36
        )
        self.confirm_entry.pack(side="left", padx=(0, 6))

        # Spacer to align with the toggle button above
        ctk.CTkFrame(conf_row, fg_color="transparent", width=36).pack(side="left")

        # ── Status + submit ───────────────────────────────────────────────
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=(0, 6))

        ctk.CTkButton(
            self, text="Crear Bóveda",
            width=200, height=38,
            command=self.on_submit
        ).pack()

    def _toggle_visibility(self):
        self._pw_visible = not self._pw_visible
        show = "" if self._pw_visible else "*"
        self.password_entry.configure(show=show)
        self.confirm_entry.configure(show=show)
        self._toggle_btn.configure(text="🙈" if self._pw_visible else "👁")

    def on_submit(self):
        p1 = self.password_entry.get()
        p2 = self.confirm_entry.get()
        if len(p1) < 4:
            self.show_message("La clave debe tener al menos 4 caracteres.", "error")
        elif p1 != p2:
            self.show_message("Las claves no coinciden.", "error")
        else:
            self.controller.handle_setup(p1)

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)