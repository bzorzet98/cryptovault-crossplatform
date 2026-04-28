import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller  = controller
        self._pw_visible = False

        # ── Back button ───────────────────────────────────────────────────
        back_bar = ctk.CTkFrame(self, fg_color="transparent")
        back_bar.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkButton(
            back_bar, text="← Volver",
            width=90, height=28,
            fg_color="transparent", border_width=1,
            border_color="#555555", text_color="#aaaaaa",
            hover_color="#333333",
            command=self.controller.app.show_welcome_view
        ).pack(side="left")

        # ── Main content ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="🔐 CryptoVault",
            font=("Roboto", 28, "bold")
        ).pack(pady=30)

        # Password row: entry + show/hide button side by side
        pw_row = ctk.CTkFrame(self, fg_color="transparent")
        pw_row.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(
            pw_row, placeholder_text="Master Password",
            show="*", width=210, height=36
        )
        self.pass_entry.pack(side="left", padx=(0, 6))
        self.pass_entry.bind("<Return>", lambda e: self.on_submit())

        self._toggle_btn = ctk.CTkButton(
            pw_row, text="👁",
            width=36, height=36,
            fg_color="#333333", hover_color="#444444",
            command=self._toggle_visibility
        )
        self._toggle_btn.pack(side="left")

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

        ctk.CTkButton(
            self, text="Desbloquear",
            command=self.on_submit
        ).pack(pady=10)

    def _toggle_visibility(self):
        self._pw_visible = not self._pw_visible
        self.pass_entry.configure(show="" if self._pw_visible else "*")
        self._toggle_btn.configure(text="🙈" if self._pw_visible else "👁")

    def on_submit(self):
        password = self.pass_entry.get()
        if password:
            self.controller.handle_login(password)
        else:
            self.show_message("Ingresa tu contraseña", "error")

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)