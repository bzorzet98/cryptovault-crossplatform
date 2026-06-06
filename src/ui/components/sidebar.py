import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
LOGO_PATH = THEME.logo  
APP_TITLE = "NOMBRE DE TU APP"

# Labels de Navegación
NAV_LABEL_ALL = "Todos los ítems"
NAV_LABEL_FAV = "Favoritos"
NAV_LABEL_SHARED = "Compartidos"
NAV_LABEL_SECURITY = "Seguridad"
NAV_LABEL_NOTES = "Notas Seguras"
NAV_LABEL_SETTINGS = "Configuración"

# Status Labels
STATUS_LABEL_UNLOCK = "Bóveda Desbloqueada"
STATUS_LABEL_SYNC = "Sincronizado"

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
SIDEBAR_WIDTH = 260
SIDEBAR_PADDING = 20
LOGO_SIZE = 45
LOGO_MARGIN_BOTTOM = 40

# Nav Item Constants
NAV_ITEM_PADDING = 12
NAV_ITEM_RADIUS = 10
NAV_ITEM_ICON_SIZE = 22
NAV_ITEM_TEXT_SIZE = 14
NAV_ITEM_SPACING = 15
NAV_HOVER_OPACITY = 0.05
NAV_SELECTED_OPACITY = 0.1

# Status Constants
STATUS_ICON_SIZE = 16
STATUS_TEXT_SIZE = 12
STATUS_SPACING = 10
STATUS_SYNC_COLOR = "green"

class Sidebar(ft.Container):
    def __init__(self):
        super().__init__(
            width=250,
            bgcolor=THEME.colors.surface,
            padding=ft.Padding.all(20),
            content=ft.Column(
                controls=[
                    # Logo
                    ft.Container(
                        content=ft.Image(src=LOGO_PATH, width=LOGO_SIZE, 
                                         height=LOGO_SIZE, fit=ft.BoxFit.CONTAIN),
                        alignment=ft.Alignment.CENTER,
                        margin=ft.Margin.only(bottom=LOGO_MARGIN_BOTTOM)
                    ),
                    # Nav Items
                    self._nav_item(ft.Icons.LOCK_OUTLINE, NAV_LABEL_ALL, selected=True),
                    self._nav_item(ft.Icons.STAR_BORDER, NAV_LABEL_FAV),
                    self._nav_item(ft.Icons.PEOPLE_OUTLINE, NAV_LABEL_SHARED),
                    self._nav_item(ft.Icons.SHIELD_OUTLINED, NAV_LABEL_SECURITY),
                    self._nav_item(ft.Icons.NOTES_OUTLINED, NAV_LABEL_NOTES),
                    self._nav_item(ft.Icons.SETTINGS_OUTLINED, NAV_LABEL_SETTINGS),
                    
                    ft.Container(expand=True), # Spacer
                    
                    # Status Area
                    ft.Column([
                        self._status_item(ft.Icons.LOCK_OPEN_OUTLINED, STATUS_LABEL_UNLOCK),
                        self._status_item(ft.Icons.CLOUD_DONE_OUTLINED, STATUS_LABEL_SYNC, color=STATUS_SYNC_COLOR),
                    ])
                ]
            )
        )

    def _nav_item(self, icon, text, selected=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=NAV_ITEM_ICON_SIZE, 
                        color="white" if selected else THEME.colors.text_secondary),
                ft.Text(text, size=NAV_ITEM_TEXT_SIZE,
                        color="white" if selected else THEME.colors.text_secondary, 
                        weight="w500")
            ],spacing=NAV_ITEM_SPACING),
            padding=ft.Padding.all(NAV_ITEM_PADDING),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.1, THEME.colors.primary) if selected else None,
            on_hover=lambda e: self._handle_hover(e),
            data=selected
        )

    def _handle_hover(self, e):
        if not e.control.data:
            e.control.bgcolor = ft.Colors.with_opacity(NAV_HOVER_OPACITY, "white") if e.data == "true" else None
            e.control.update()


    def _status_item(self, icon, text, color="white"):
        return ft.Row([
            ft.Icon(icon, size=STATUS_ICON_SIZE, color=color),
            ft.Text(text, size=STATUS_TEXT_SIZE, color=THEME.colors.text_secondary)
        ], spacing=STATUS_SPACING)