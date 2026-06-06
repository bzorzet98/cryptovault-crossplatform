import flet as ft
from src.config import THEME
from src.ui.components.cards import RecentFileCard, ActionCard

# ==========================================
# --- 1. APP ASSETS & TEXT CONSTANTS ---
# ==========================================
LOGO_PATH = THEME.logo2
NAV_TITLE = "Gestor de Sesiones"
NAV_SUBTITLE = "Selecciona un archivo\npara continuar"

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
SIDEBAR_WIDTH = 280
SIDEBAR_PADDING = 30
CONTENT_PADDING = 40
CARD_AREA_PADDING = 30
CARD_AREA_RADIUS = 16
COL_SPACING = 40
SECTION_SPACING = 15
HEADER_SPACING = 40

LOGO_WIDTH = 180
SECTION_TITLE_SIZE = 18
NAV_TITLE_SIZE = 14
NAV_SUBTITLE_SIZE = 12
FOOTER_TEXT_SIZE = 11

ICON_NAV_SIZE = 18
ICON_SECTION_SIZE = 20
ICON_FOOTER_SIZE = 16

BG_OPACITY = 0.02
BORDER_OPACITY = 0.05

class SessionManagerView(ft.View):
    def __init__(self, page: ft.Page, on_file_selected=None, on_create_new=None, test_mode=False):
        super().__init__(route="/sessions", bgcolor=THEME.colors.bg, padding=0)
        self.page_ref = page
        self.on_file_selected = on_file_selected
        self.on_create_new = on_create_new
        self.test_mode = test_mode
        self.recent_files = [] if self.test_mode else [
            {"icon": ft.Icons.DESKTOP_WINDOWS, "title": "Finanzas_2024.json", "path": "C:\\Docs\\Finanzas.json", "time": "Hoy, 09:42"},
            {"icon": ft.Icons.CLOUD_QUEUE, "title": "Personal.json", "path": "Drive / Personal.json", "time": "Ayer, 18:30"}
        ]

        # El init ahora es super limpio:
        self.expand = True
        self.controls = [self._build_main_layout()]

    def _build_main_layout(self):
        """Construye el layout principal de la vista."""
        return ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                self._build_sidebar(),
                self._build_content_area()
            ]
        )
    
    def _build_sidebar(self):
        return ft.Container(
            width=SIDEBAR_WIDTH,
            padding=SIDEBAR_PADDING,
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=LOGO_WIDTH, fit=ft.BoxFit.CONTAIN),
                ft.Container(height=HEADER_SPACING),
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_OUTLINED, color=THEME.colors.primary, size=ICON_NAV_SIZE),
                    ft.Text(NAV_TITLE, size=NAV_TITLE_SIZE, color=THEME.colors.primary, weight="bold"),
                ]),
                ft.Text(NAV_SUBTITLE, size=NAV_SUBTITLE_SIZE, color=THEME.colors.text_secondary)
            ])
        )

    def _build_content_area(self):
        return ft.Container(
            expand=True,
            padding=CONTENT_PADDING,
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(BG_OPACITY, THEME.colors.text_main),
                border_radius=CARD_AREA_RADIUS,
                border=ft.Border.all(1, ft.Colors.with_opacity(BORDER_OPACITY, THEME.colors.text_main)),
                padding=CARD_AREA_PADDING,
                content=ft.Row([
                    self._build_recent_files_column_wrapper(), # Columna 1
                    ft.Container(width=COL_SPACING),
                    self._build_actions_column()               # Columna 2
                ])
            )
        )

    def _build_recent_files_column_wrapper(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ACCESS_TIME, size=ICON_SECTION_SIZE, color=THEME.colors.text_main),
                ft.Text("Archivos Recientes", size=SECTION_TITLE_SIZE, weight="bold", color=THEME.colors.text_main)
            ]),
            ft.Container(height=SECTION_SPACING),
            self._build_recent_files_column(),
        ], expand=3)

    def _build_actions_column(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LINK, size=ICON_SECTION_SIZE, color=THEME.colors.text_main),
                ft.Text("Conexiones", size=SECTION_TITLE_SIZE, weight="bold", color=THEME.colors.text_main)
            ]),
            ft.Container(height=SECTION_SPACING),
            ActionCard(icon=ft.Icons.FOLDER_OPEN, title="Examinar PC", subtitle="Selecciona un archivo local"),
            ActionCard(icon=ft.Icons.CLOUD_OUTLINED, title="Google Drive", subtitle="Conecta tu cuenta", is_primary=True),
            ActionCard(icon=ft.Icons.ADD, title="Nuevo Archivo", subtitle="Crea uno nuevo", on_click=self.on_create_new),
            ft.Container(expand=True),
            ft.Row([
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=ICON_FOOTER_SIZE, color=THEME.colors.text_secondary),
                ft.Text("Tus datos permanecen cifrados\nde extremo a extremo.", size=FOOTER_TEXT_SIZE, color=THEME.colors.text_secondary)
            ], width=250)
        ], expand=2)

    def _build_recent_files_column(self):
        """Muestra tarjetas o un estado vacío si no hay archivos."""
        if not self.recent_files:
            return ft.Column([
                ft.Container(height=60),
                ft.Icon(ft.Icons.FOLDER_OFF_OUTLINED, size=60, color=THEME.colors.text_secondary),
                ft.Text("Sin archivos recientes", size=16, color=THEME.colors.text_secondary),
                ft.Text("Abre o crea una bóveda para empezar.", size=12, color=THEME.colors.text_secondary),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        
        return ft.Column([
            *[RecentFileCard(
                icon=f["icon"], title=f["title"], path=f["path"], last_seen=f["time"],
                on_click=lambda e, name=f["title"]: self._trigger_selection(name)
            ) for f in self.recent_files]
        ], expand=True)

    def _trigger_selection(self, file_name):
        if self.on_file_selected:
            self.on_file_selected(file_name)