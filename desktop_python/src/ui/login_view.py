import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # --- BOTÓN DE VOLVER (Arriba a la izquierda) ---
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

        # --- CONTENIDO PRINCIPAL ---
        ctk.CTkLabel(self, text="🔐 CryptoVault", font=("Roboto", 28, "bold")).pack(pady=30)

        self.pass_entry = ctk.CTkEntry(
            self, placeholder_text="Master Password", show="*", width=250
        )
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", lambda e: self.on_submit())

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

        ctk.CTkButton(self, text="Desbloquear", command=self.on_submit).pack(pady=10)

    def on_submit(self):
        password = self.pass_entry.get()
        if password:
            self.controller.handle_login(password)
        else:
            self.show_message("Ingresa tu contraseña", "error")

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)