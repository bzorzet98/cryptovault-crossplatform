import flet as ft
from src.config import THEME
from src.ui.components.sidebar import Sidebar
from src.ui.components.setting_card import SettingCard

# ==========================================
# --- APP TEXT CONSTANTS ---
# ==========================================
TITLE = "Configuración"
SUBTITLE = "Personaliza tu experiencia y administra tu bóveda."
HELP_TEXT = "¿Necesitas ayuda? Consulta nuestra"
HELP_LINK_TEXT = "guía de seguridad."

# ==========================================
# --- LAYOUT & SIZING CONSTANTS ---
# ==========================================
CONTENT_PADDING = 40
MAIN_ROW_SPACING = 0
HEADER_SPACER_HEIGHT = 30
CARD_SPACER_HEIGHT = 10
SPACING_SMALL = 5
SPACING_NORMAL = 10
SPACING_MEDIUM = 15
SPACING_LARGE = 20
SPACING_XLARGE = 30
TEXT_SIZE_TITLE = 32
TEXT_SIZE_SUBTITLE = 16
TEXT_SIZE_NORMAL = 14
TEXT_SIZE_FOOTER = 13
TEXT_SIZE_SMALL = 12
ICON_SIZE_SMALL = 16
ICON_SIZE_MEDIUM = 18
BUTTON_RADIUS = 8


class SettingsView(ft.View):
    def __init__(self, page: ft.Page, 
                 # Acciones propias de la vista
                 on_sync_change=None, on_theme_change=None, 
                 on_export_click=None, on_delete_click=None,
                 # Acciones de Navegación (Sidebar)
                 on_all_click=None, on_fav_click=None, 
                 on_shared_click=None, on_security_click=None, 
                 on_notes_click=None, on_settings_click=None):
        
        super().__init__(
            route="/settings",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page

        # --- CONTROLES DE ACCIÓN ---
        
        self.sync_switch = ft.Row([
            ft.Text("Google Drive", size=TEXT_SIZE_NORMAL),
            ft.Switch(
                value=True, 
                active_color=THEME.colors.primary,
                on_change=on_sync_change  
            )
        ], spacing=SPACING_LARGE)

        self.appearance_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Row([ft.Radio(value="dark"), ft.Text("Oscuro"), ft.Icon(ft.Icons.DARK_MODE, size=ICON_SIZE_SMALL)], spacing=SPACING_SMALL),
                ft.Row([ft.Radio(value="light"), ft.Text("Claro"), ft.Icon(ft.Icons.LIGHT_MODE, size=ICON_SIZE_SMALL)], spacing=SPACING_SMALL),
            ], spacing=SPACING_XLARGE),
            value="dark",
            on_change=on_theme_change  
        )

        self.danger_buttons = ft.Row([
            ft.OutlinedButton(
                content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=ICON_SIZE_MEDIUM), ft.Text("Exportar JSON")]),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_RADIUS)),
                on_click=on_export_click  
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.DELETE_OUTLINE, size=ICON_SIZE_MEDIUM), ft.Text("Eliminar Bóveda")]),
                bgcolor=ft.Colors.RED_700,
                color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BUTTON_RADIUS)),
                on_click=on_delete_click  
            )
        ], spacing=SPACING_MEDIUM)

        # --- ESTRUCTURA DE LA VISTA ---
        self.controls = [
            ft.Row(
                expand=True,
                spacing=MAIN_ROW_SPACING,
                controls=[
                    # Pasamos los callbacks de navegación hacia abajo al Sidebar
                    Sidebar(
                        on_all_click=on_all_click,
                        on_fav_click=on_fav_click,
                        on_shared_click=on_shared_click,
                        on_security_click=on_security_click,
                        on_notes_click=on_notes_click,
                        on_settings_click=on_settings_click
                    ), 
                    
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.all(CONTENT_PADDING),
                        content=ft.Column([
                            ft.Text(TITLE, size=TEXT_SIZE_TITLE, weight="bold", color="white"),
                            ft.Text(SUBTITLE, size=TEXT_SIZE_SUBTITLE, color=THEME.colors.text_secondary),
                            ft.Container(height=HEADER_SPACER_HEIGHT),

                            SettingCard(
                                icon=ft.Icons.CLOUD_QUEUE,
                                title="Sincronización en la nube",
                                description="Sincroniza tu bóveda de forma segura con Google Drive.",
                                action_control=self.sync_switch
                            ),
                            ft.Container(height=CARD_SPACER_HEIGHT),
                            
                            SettingCard(
                                icon=ft.Icons.PALETTE_OUTLINED,
                                title="Apariencia",
                                description="Elige el tema de la aplicación.",
                                action_control=ft.Column([
                                    ft.Text("Tema de la aplicación", size=TEXT_SIZE_SMALL, color=THEME.colors.text_secondary),
                                    self.appearance_radio
                                ], spacing=SPACING_NORMAL)
                            ),
                            ft.Container(height=CARD_SPACER_HEIGHT),

                            SettingCard(
                                icon=ft.Icons.WARNING_AMBER_ROUNDED,
                                title="Zona de peligro",
                                description="Estas acciones son permanentes y no se pueden deshacer.",
                                action_control=ft.Column([
                                    ft.Text("Administración de datos", size=TEXT_SIZE_SMALL, color=THEME.colors.text_secondary, text_align="right"),
                                    self.danger_buttons
                                ], spacing=SPACING_NORMAL, horizontal_alignment="end")
                            ),

                            ft.Container(expand=True),

                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=ICON_SIZE_SMALL, color=THEME.colors.text_secondary),
                                ft.Text(HELP_TEXT, size=TEXT_SIZE_FOOTER, color=THEME.colors.text_secondary),
                                ft.Text(HELP_LINK_TEXT, size=TEXT_SIZE_FOOTER, color=THEME.colors.primary, italic=True),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=SPACING_SMALL)
                        ])
                    )
                ]
            )
        ]