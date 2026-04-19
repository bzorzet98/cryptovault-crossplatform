import customtkinter as ctk

class SetupView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Configuración Inicial", font=("Roboto", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Crea tu Master Password para cifrar tus datos.").pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Nueva Password", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.confirm_entry = ctk.CTkEntry(self, placeholder_text="Confirmar Password", show="*", width=250)
        self.confirm_entry.pack(pady=10)

        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

        ctk.CTkButton(self, text="Crear Bóveda", command=self.on_submit).pack(pady=20)

    def on_submit(self):
        p1 = self.password_entry.get()
        p2 = self.confirm_entry.get()
        if p1 == p2 and len(p1) >= 4:
            # Llamamos al Orchestrator
            self.controller.handle_setup(p1)
        else:
            self.show_message("Las claves no coinciden o son muy cortas", "error")

    def show_message(self, text, msg_type="info"):
        color = "red" if msg_type == "error" else "green"
        self.message_label.configure(text=text, text_color=color)