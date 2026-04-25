import customtkinter as ctk
import os

class WelcomeView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="¡Bienvenido a CryptoVault!", font=("Roboto", 24, "bold")).pack(pady=40)
        
        ctk.CTkLabel(self, text="¿Cómo deseas ingresar?", justify="center").pack(pady=10)

        # OPCIÓN 1: DRIVE (Recuperar o forzar descarga de la nube)
        self.btn_drive = ctk.CTkButton(
            self, text="Conectar con Google Drive", 
            command=self.controller.handle_drive_connection,
            fg_color="#2c8558", hover_color="#1e5c3d"
        )
        self.btn_drive.pack(pady=20, padx=50, fill="x")

        # OPCIÓN 2: LOCAL DINÁMICO (Crear o Abrir)
        # Evaluamos si ya existe una bóveda física en la PC
        vault_exists = os.path.exists(self.controller.vault_path)
        
        # Cambiamos el texto y la función del botón según si existe o no
        btn_text = "Abrir Bóveda Local" if vault_exists else "Crear Bóveda Local (Solo PC)"
        btn_cmd = self.controller.app.show_login_view if vault_exists else self.controller.app.show_setup_view

        self.btn_local = ctk.CTkButton(
            self, text=btn_text, 
            command=btn_cmd,
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
            self.btn_drive.configure(state="disabled")
            self.btn_local.configure(state="disabled")
            self.btn_readonly.configure(state="disabled")
            self.loading_label.configure(text="Conectando... por favor espera.")
        else:
            self.btn_drive.configure(state="normal")
            self.btn_local.configure(state="normal")
            self.btn_readonly.configure(state="normal")
            self.loading_label.configure(text="")