import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
LOGO_PATH = THEME.shield  
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
SIDEBAR_WIDTH = 300
SIDEBAR_PADDING = 20
LOGO_SIZE = 190
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
    def __init__(self, 
                 on_all_click=None, 
                 on_fav_click=None, 
                 on_shared_click=None, 
                 on_security_click=None, 
                 on_notes_click=None, 
                 on_settings_click=None):
        
        super().__init__(
            width=SIDEBAR_WIDTH,
            bgcolor=THEME.colors.surface,
            padding=ft.Padding.all(SIDEBAR_PADDING),
            content=ft.Column(
                controls=[
                    # Logo
                    ft.Container(
                        content=ft.Image(src=LOGO_PATH, width=LOGO_SIZE, 
                                         height=LOGO_SIZE, fit=ft.BoxFit.CONTAIN),
                        alignment=ft.Alignment.CENTER,
                        margin=ft.Margin.only(bottom=LOGO_MARGIN_BOTTOM)
                    ),
                    # Nav Items - ¡Aquí conectamos los callbacks!
                    self._nav_item(ft.Icons.LOCK_OUTLINE, NAV_LABEL_ALL, selected=True, on_click=on_all_click),
                    self._nav_item(ft.Icons.STAR_BORDER, NAV_LABEL_FAV, on_click=on_fav_click),
                    self._nav_item(ft.Icons.PEOPLE_OUTLINE, NAV_LABEL_SHARED, on_click=on_shared_click),
                    self._nav_item(ft.Icons.SHIELD_OUTLINED, NAV_LABEL_SECURITY, on_click=on_security_click),
                    self._nav_item(ft.Icons.NOTES_OUTLINED, NAV_LABEL_NOTES, on_click=on_notes_click),
                    self._nav_item(ft.Icons.SETTINGS_OUTLINED, NAV_LABEL_SETTINGS, on_click=on_settings_click),
                    
                    ft.Container(expand=True), # Spacer
                    
                    # Status Area
                    ft.Column([
                        self._status_item(ft.Icons.LOCK_OPEN_OUTLINED, STATUS_LABEL_UNLOCK),
                        self._status_item(ft.Icons.CLOUD_DONE_OUTLINED, STATUS_LABEL_SYNC, color=STATUS_SYNC_COLOR),
                    ])
                ]
            )
        )

    # Añadimos el parámetro on_click aquí
    def _nav_item(self, icon, text, selected=False, on_click=None):
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
            on_click=on_click,  # <-- Conectamos la acción al contenedor
            ink=True,           # <-- Activa el efecto de onda (ripple) al hacer clic
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