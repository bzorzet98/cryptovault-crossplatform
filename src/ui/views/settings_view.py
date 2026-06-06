import flet as ft
from src.config import THEME
from src.ui.components.sidebar import Sidebar
from src.ui.components.setting_card import SettingCard

# ==========================================
# --- APP TEXT CONSTANTS ---
# ==========================================
TITLE = "Configuración"
SUBTITLE = "Personaliza tu experiencia y administra tu bóveda."
HELP_TEXT = "¿Necesitas ayuda? Consulta nuestra guía de seguridad."

class SettingsView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/settings",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page

        # --- CONTROLES DE ACCIÓN ---
        
        # 1. Sync Switch
        self.sync_switch = ft.Row([
            ft.Text("Google Drive", size=14),
            ft.Switch(value=True, active_color=THEME.colors.primary)
        ], spacing=20)

        # 2. Appearance Radio
        self.appearance_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Row([ft.Radio(value="dark"), ft.Text("Oscuro"), ft.Icon(ft.Icons.DARK_MODE, size=16)], spacing=5),
                ft.Row([ft.Radio(value="light"), ft.Text("Claro"), ft.Icon(ft.Icons.LIGHT_MODE, size=16)], spacing=5),
            ], spacing=30),
            value="dark"
        )

        # 3. Danger Zone Buttons
        self.danger_buttons = ft.Row([
            ft.OutlinedButton(
                content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=18), ft.Text("Exportar JSON")]),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.DELETE_OUTLINE, size=18), ft.Text("Eliminar Bóveda")]),
                bgcolor=ft.Colors.RED_700,
                color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
            )
        ], spacing=15)

        # --- ESTRUCTURA DE LA VISTA ---
        self.controls = [
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    Sidebar(), # Reutilizamos tu sidebar
                    
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.all(40),
                        content=ft.Column([
                            # Header
                            ft.Text(TITLE, size=32, weight="bold", color="white"),
                            ft.Text(SUBTITLE, size=16, color=THEME.colors.text_secondary),
                            ft.Container(height=30),

                            # Config Sections
                            SettingCard(
                                icon=ft.Icons.CLOUD_QUEUE,
                                title="Sincronización en la nube",
                                description="Sincroniza tu bóveda de forma segura con Google Drive.",
                                action_control=self.sync_switch
                            ),
                            ft.Container(height=10),
                            
                            SettingCard(
                                icon=ft.Icons.PALETTE_OUTLINED,
                                title="Apariencia",
                                description="Elige el tema de la aplicación.",
                                action_control=ft.Column([
                                    ft.Text("Tema de la aplicación", size=12, color=THEME.colors.text_secondary),
                                    self.appearance_radio
                                ], spacing=10)
                            ),
                            ft.Container(height=10),

                            SettingCard(
                                icon=ft.Icons.WARNING_AMBER_ROUNDED,
                                title="Zona de peligro",
                                description="Estas acciones son permanentes y no se pueden deshacer.",
                                action_control=ft.Column([
                                    ft.Text("Administración de datos", size=12, color=THEME.colors.text_secondary, text_align="right"),
                                    self.danger_buttons
                                ], spacing=10, horizontal_alignment="end")
                            ),

                            ft.Container(expand=True), # Spacer para empujar el footer

                            # Footer Help
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=THEME.colors.text_secondary),
                                ft.Text(HELP_TEXT, size=13, color=THEME.colors.text_secondary),
                                ft.Text("guía de seguridad", size=13, color=THEME.colors.primary, italic=True),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
                        ])
                    )
                ]
            )
        ]