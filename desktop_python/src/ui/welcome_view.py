import customtkinter as ctk

class WelcomeView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="¡Bienvenido a CryptoVault!", font=("Roboto", 24, "bold")).pack(pady=40)
        
        ctk.CTkLabel(self, text="Parece que es tu primera vez aquí.\n¿Cómo quieres empezar?", 
                     justify="center").pack(pady=10)

        # OPCIÓN 1: DRIVE (Recuperar o nueva nube)
        self.btn_drive = ctk.CTkButton(
            self, text="Conectar con Google Drive", 
            command=self.controller.handle_drive_connection,
            fg_color="#2c8558", hover_color="#1e5c3d"
        )
        self.btn_drive.pack(pady=20, padx=50, fill="x")

        # OPCIÓN 2: LOCAL (Privacidad total)
        self.btn_local = ctk.CTkButton(
            self, text="Crear Bóveda Local (Solo PC)", 
            command=self.controller.app.show_setup_view,
            fg_color="transparent", border_width=2
        )
        self.btn_local.pack(pady=10, padx=50, fill="x")

        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.pack(pady=10)

        # OPCIÓN 3: SOLO LECTURA
        self.btn_readonly = ctk.CTkButton(
            self, text="Modo Solo Lectura (Offline)", 
            command=self.controller.handle_readonly_setup,
            fg_color="#555555", hover_color="#333333"
        )
        self.btn_readonly.pack(pady=10, padx=50, fill="x")
        
    def toggle_loading(self, is_loading):
        if is_loading:
            self.btn_drive.configure(state="disabled", text="Buscando en la nube...")
        else:
            self.btn_drive.configure(state="normal", text="Conectar con Google Drive")

    def show_message(self, text, msg_type="info"):
        color = "red" if msg_type == "error" else "white"
        self.loading_label.configure(text=text, text_color=color)