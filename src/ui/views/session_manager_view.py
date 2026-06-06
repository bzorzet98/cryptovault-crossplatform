import flet as ft
from src.config import THEME
# Importamos tus componentes
from src.ui.components.cards import RecentFileCard, ActionCard

# ==============================================================================
# --- CONSTANTES GLOBALES DE DISEÑO ---
# ==============================================================================
LOGO_PATH = THEME.logo2
SIDEBAR_WIDTH = 280
SIDEBAR_PADDING = 20
CONTENT_PADDING = 40
SECTION_SPACING = 20
HEADER_SPACING = 40
LOGO_WIDTH = 180
SECTION_TITLE_SIZE = 18
NAV_TITLE_SIZE = 14

class SessionManagerView(ft.View):
    def __init__(self, page: ft.Page, recent_files=None, 
                 on_load_local=None, on_load_drive=None, 
                 on_create_new=None, on_settings=None, 
                 on_file_selected=None):
        super().__init__(
            route="/sessions",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page
        self.recent_files = recent_files if recent_files else []
        
        # Callbacks
        self.on_load_local = on_load_local
        self.on_load_drive = on_load_drive
        self.on_create_new = on_create_new
        self.on_settings = on_settings
        self.on_file_selected = on_file_selected

        self.controls = [self._build_main_layout()]

    def _build_main_layout(self):
        return ft.Row(
            expand=True,
            controls=[
                self._build_sidebar(),
                self._build_content_area()
            ]
        )

    def _build_sidebar(self):
        return ft.Container(
            width=SIDEBAR_WIDTH,
            padding=SIDEBAR_PADDING,
            bgcolor=ft.Colors.with_opacity(0.03, THEME.colors.text_main), # Sutil fondo para diferenciar
            content=ft.Column([
                # Logo
                ft.Container(
                    content=ft.Image(src=LOGO_PATH, width=LOGO_WIDTH, fit=ft.BoxFit.CONTAIN),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.only(top=20, bottom=20)
                ),
                ft.Container(height=HEADER_SPACING),
                
                # Secciones de Acciones usando tus ActionCards
                ft.Text("ACCIONES", size=12, weight="bold", color=THEME.colors.text_secondary),
                ft.Container(height=10),
                
                ActionCard(
                    icon=ft.Icons.FOLDER_OPEN, 
                    title="Examinar PC", 
                    subtitle="Abrir archivo local", 
                    on_click=self.on_load_local
                ),
                ActionCard(
                    icon=ft.Icons.CLOUD_OUTLINED, 
                    title="Google Drive", 
                    subtitle="Conectar cuenta", 
                    on_click=self.on_load_drive
                ),
                ActionCard(
                    icon=ft.Icons.ADD, 
                    title="Nueva Bóveda", 
                    subtitle="Crear desde cero", 
                    is_primary=True, # Destacamos la creación
                    on_click=self.on_create_new
                ),
                
                ft.Container(expand=True),
                
                # Preferencias (Usamos un ActionCard simple o un Tile)
                ft.Divider(color=THEME.colors.text_secondary, opacity=0.2),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS_OUTLINED),
                    title=ft.Text("Preferencias", size=14),
                    on_click=self.on_settings
                )
            ])
        )

    def _build_content_area(self):
        return ft.Container(
            expand=True,
            padding=CONTENT_PADDING,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=20, color=THEME.colors.text_main),
                    ft.Text("Archivos Recientes", size=SECTION_TITLE_SIZE, weight="bold", color=THEME.colors.text_main)
                ]),
                ft.Container(height=SECTION_SPACING),
                
                # Lista dinámica
                ft.Column(
                    controls=[
                        RecentFileCard(
                            icon=f.get("icon", ft.Icons.INSERT_DRIVE_FILE),
                            title=f.get("title", "Sin título"),
                            path=f.get("path", "Sin ruta"),
                            last_seen=f.get("last_seen", "Desconocido"), # Normalizado a 'last_seen'
                            on_click=lambda e, name=f.get("title"): self._trigger_selection(name)
                        ) for f in self.recent_files
                    ] if self.recent_files else [ft.Text("No hay archivos recientes.", color=THEME.colors.text_secondary)]
                )
            ])
        )

    def _trigger_selection(self, file_name):
        if self.on_file_selected:
            self.on_file_selected(file_name)