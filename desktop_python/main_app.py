import customtkinter as ctk
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.logic.orchestrator import VaultOrchestrator
from src.ui.login_view       import LoginView
from src.ui.setup_view       import SetupView
from src.ui.dashboard_view   import DashboardView
from src.ui.welcome_view     import WelcomeView
from src.ui.loading_view     import LoadingView
from src.ui.exit_view        import ExitView
from src.ui.drive_select_view import DriveSelectView


class CryptoVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CryptoVault Desktop")
        self.geometry("480x680")
        ctk.set_appearance_mode("dark")

        self.current_view = None
        self.orchestrator = VaultOrchestrator(self)

        # Intercept window X button
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self.orchestrator.start_app()

    def _on_window_close(self):
        if self.orchestrator.master_key is not None:
            self.orchestrator.handle_exit(then_quit=True)
        else:
            self.destroy()

    # ── helpers ───────────────────────────────────────────────────────────

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    # ── navigation ────────────────────────────────────────────────────────

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
        self.current_view = SetupView(self, controller=self.orchestrator)
        self.current_view.pack(fill="both", expand=True)

    def show_login_view(self):
        self.clear_view()
        self.current_view = LoginView(self, controller=self.orchestrator)
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard_view(self, vault_data):
        self.clear_view()
        self.current_view = DashboardView(
            self, controller=self.orchestrator, data=vault_data
        )
        self.current_view.pack(fill="both", expand=True)

    def show_drive_select_view(self, vaults: list):
        """Picker shown after Drive auth, lists .data files for the user to choose."""
        self.clear_view()
        self.current_view = DriveSelectView(
            self, controller=self.orchestrator, vaults=vaults
        )
        self.current_view.pack(fill="both", expand=True)

    def show_exit_view(self, mode: str = "QUIT"):
        """
        mode: "QUIT"   → user wants to close the whole app
              "LOGOUT" → user wants to go back to the menu
        """
        self.clear_view()
        self.current_view = ExitView(self, controller=self.orchestrator, mode=mode)
        self.current_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = CryptoVaultApp()
    app.mainloop()