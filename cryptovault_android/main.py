from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

from src.logic.orchestrator import VaultOrchestrator


class CryptoVaultApp(App):
    def build(self):
        # Dark background globally
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        self.sm = ScreenManager(transition=NoTransition())
        self.orchestrator = VaultOrchestrator(app=self)

        self.orchestrator.start_app()
        return self.sm

    # ── Navigation (mirrors desktop show_X_view methods) ──────────────────

    def show_welcome_screen(self):
        from src.ui.welcome_screen import WelcomeScreen
        self._switch("welcome", WelcomeScreen)

    def show_login_screen(self):
        from src.ui.login_screen import LoginScreen
        self._switch("login", LoginScreen)

    def show_setup_screen(self):
        from src.ui.setup_screen import SetupScreen
        self._switch("setup", SetupScreen)

    def show_dashboard_screen(self, vault_data):
        from src.ui.dashboard_screen import DashboardScreen
        screen = self._switch("dashboard", DashboardScreen)
        screen.load_vault(vault_data)

    def show_drive_select_screen(self, vaults):
        from src.ui.drive_select_screen import DriveSelectScreen
        screen = self._switch("drive_select", DriveSelectScreen)
        screen.load_vaults(vaults)

    def show_loading_screen(self, message="Cargando..."):
        from src.ui.loading_screen import LoadingScreen
        screen = self._switch("loading", LoadingScreen)
        screen.set_message(message)

    # ── Internal helper ───────────────────────────────────────────────────

    def _switch(self, name, screen_class):
        """Remove old screen if exists, create fresh, switch to it."""
        if self.sm.has_screen(name):
            self.sm.remove_widget(self.sm.get_screen(name))
        screen = screen_class(name=name, controller=self.orchestrator)
        self.sm.add_widget(screen)
        self.sm.current = name
        return screen


if __name__ == "__main__":
    CryptoVaultApp().run()