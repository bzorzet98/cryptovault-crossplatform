import customtkinter as ctk
import os
import sys

# Asegurar que Python encuentre la carpeta 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.logic.orchestrator import VaultOrchestrator
from src.ui.login_view import LoginView
from src.ui.setup_view import SetupView
from src.ui.dashboard_view import DashboardView
from src.ui.welcome_view import WelcomeView
from src.ui.loading_view import LoadingView

class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CryptoVault Desktop")
        self.geometry("450x650")
        ctk.set_appearance_mode("dark")
        
        self.current_view = None
        
        # Iniciar el Cerebro (Orchestrator) pasándole esta ventana como raíz
        self.orchestrator = VaultOrchestrator(self)
        
        # Arrancar la lógica
        self.orchestrator.start_app()

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()
            
    def show_welcome_view(self):
        self.clear_view()
        self.current_view = WelcomeView(self, controller=self.orchestrator)
        self.current_view.pack(fill="both", expand=True)
        
    def show_loading_view(self):
        self.clear_view()
        self.current_view = LoadingView(self)
        self.current_view.pack(fill="both", expand=True)
        
    def show_setup_view(self):
        self.clear_view()
        # Le pasamos el orquestador (controller) a la vista
        self.current_view = SetupView(self, controller=self.orchestrator)
        self.current_view.pack(fill="both", expand=True)

    def show_login_view(self):
        self.clear_view()
        self.current_view = LoginView(self, controller=self.orchestrator)
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard_view(self, vault_data):
        self.clear_view()
        self.current_view = DashboardView(self, controller=self.orchestrator, data=vault_data)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()