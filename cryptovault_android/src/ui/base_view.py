# Example of the Standard Pattern for src/ui/base_view.py (Logic)
import customtkinter as ctk

class BaseView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller  # This is the Orchestrator

    def render(self, data=None):
        """Method to update the UI with new information."""
        pass

    def get_input(self):
        """Method to extract data from fields."""
        pass

    def toggle_loading(self, is_loading: bool):
        """Standard way to disable buttons during async tasks."""
        pass