import customtkinter as ctk

class LoadingView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0)

        # Spinner animado (simulado con texto o un label)
        self.title_label = ctk.CTkLabel(self.container, text="CryptoVault", font=("Roboto", 28, "bold"))
        self.title_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.container, width=300)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.container, text="Iniciando...", font=("Roboto", 14))
        self.status_label.pack(pady=10)

    def update_status(self, message, progress):
        """Actualiza el mensaje y la barra de progreso (0.0 a 1.0)."""
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)
        self.update_idletasks() # Forzar actualización visual en Tkinter