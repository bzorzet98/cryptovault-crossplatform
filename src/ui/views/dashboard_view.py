import flet as ft
from src.config import THEME
from src.ui.components.sidebar import Sidebar
from src.ui.components.item_card import ItemCard
from src.ui.components.search_bar import SearchBar
from src.ui.components.detail_view import DetailView

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
TITLE_TEXT = "Todos los ítems"
BTN_ADD_TEXT = "Añadir ítem"
TOOLTIP_SYNC = "Sincronizar ahora"

# ==========================================
# --- 2. LAYOUT & SIZING CONSTANTS ---
# ==========================================
# Espaciados y Paddings
MAIN_PADDING = 35
TOP_BAR_SPACING = 20
CONTENT_DIVIDER_WIDTH = 20
LIST_COLUMN_EXPAND = 6  # Proporción de la lista vs el detalle
ITEMS_SPACING = 10
SPACER_HEIGHT = 20

# Tamaños de Fuente e Iconos
TITLE_SIZE = 28
ADD_BTN_RADIUS = 8

class DashboardView(ft.View):
    def __init__(self, page: ft.Page, items=None,
                 # Acciones de la vista
                 on_search=None, on_sync_click=None, on_add_click=None, on_item_select=None,
                 # Acciones de navegación (Sidebar)
                 on_all_click=None, on_fav_click=None, on_shared_click=None,
                 on_security_click=None, on_notes_click=None, on_settings_click=None):
        
        super().__init__(
            route="/dashboard",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page
        
        # Datos inyectados
        self.items_data = items if items else []
        
        # Guardamos los callbacks externos
        self.on_search_callback = on_search
        self.on_sync_callback = on_sync_click
        self.on_add_callback = on_add_click
        self.on_item_select_callback = on_item_select

        # INSTANCIAR COMPONENTES
        self.sidebar = Sidebar(
            on_all_click=on_all_click,
            on_fav_click=on_fav_click,
            on_shared_click=on_shared_click,
            on_security_click=on_security_click,
            on_notes_click=on_notes_click,
            on_settings_click=on_settings_click
        )
        self.search_bar = SearchBar(on_change=self.handle_search)
        self.details = DetailView()
        self.items_column = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE, 
            expand=True, 
            spacing=ITEMS_SPACING
        )

        # ESTRUCTURA PRINCIPAL
        self.controls = [
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    # 1. BARRA LATERAL
                    self.sidebar,
                    
                    # 2. CONTENIDO PRINCIPAL
                    ft.Container(
                        expand=True,
                        padding=MAIN_PADDING,
                        content=ft.Column([
                            
                            # CABECERA (Título + Búsqueda + Acciones)
                            ft.Row([
                                ft.Text(
                                    TITLE_TEXT, 
                                    size=TITLE_SIZE, 
                                    weight="bold", 
                                    expand=True,
                                    color="white"
                                ),
                                self.search_bar,
                                ft.IconButton(
                                    icon=ft.Icons.CLOUD_DONE_OUTLINED, 
                                    icon_color=THEME.colors.text_secondary, 
                                    tooltip=TOOLTIP_SYNC,
                                    on_click=self.handle_sync_click # Vinculado a la función local
                                ),
                                ft.ElevatedButton(
                                    BTN_ADD_TEXT, 
                                    icon=ft.Icons.ADD, 
                                    bgcolor=THEME.colors.primary, 
                                    color="white",
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=ADD_BTN_RADIUS)
                                    ),
                                    on_click=self.handle_add_click # Vinculado a la función local
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            
                            ft.Container(height=SPACER_HEIGHT), 
                            
                            # ÁREA DE TRABAJO (Lista | Detalles)
                            ft.Row([
                                ft.Column([self.items_column], expand=LIST_COLUMN_EXPAND),
                                ft.VerticalDivider(width=CONTENT_DIVIDER_WIDTH, color="transparent"),
                                self.details
                            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
                        ])
                    )
                ]
            )
        ]
        
        # Renderizamos los datos
        self._render_items()

    # ==========================================
    # --- FUNCIONES DE ACCIÓN LOCALES ---
    # ==========================================

    def _render_items(self):
        """Genera las tarjetas iterando sobre la data recibida."""
        if self.items_data:
            for item in self.items_data:
                self.items_column.controls.append(
                    ItemCard(
                        title=item.get("title", "Sin título"), 
                        subtitle=item.get("subtitle", ""), 
                        is_fav=item.get("is_fav", False),
                        on_click=lambda e, data=item: self.handle_item_selected(data)
                    )
                )
        else:
            self.items_column.controls.append(
                ft.Text("No hay ítems para mostrar.", color=THEME.colors.text_secondary)
            )

    def handle_item_selected(self, item_data):
        """Lógica de comunicación entre la lista y el panel de detalles."""
        print(f"[DashboardView] Actualizando detalles para: {item_data.get('title')}")
        
        # Actualiza visualmente el panel derecho interno
        self.details.update_details(
            title=item_data.get("title", ""),
            username=item_data.get("username", ""),
            password=item_data.get("password", ""),
            website=item_data.get("website", ""),
            notes=item_data.get("notes", "")
        )
        
        # Si el test/controlador principal necesita saber qué se clickeó
        if self.on_item_select_callback:
            self.on_item_select_callback(item_data)

    def handle_search(self, e):
        """Manejador del evento de búsqueda."""
        query = e.data
        print(f"[DashboardView] Escribiendo en búsqueda: {query}")
        if self.on_search_callback:
            self.on_search_callback(query)

    def handle_sync_click(self, e):
        """Manejador del botón de sincronización."""
        print("[DashboardView] Botón 'Sincronizar' presionado.")
        if self.on_sync_callback:
            self.on_sync_callback(e)

    def handle_add_click(self, e):
        """Manejador del botón para crear un nuevo registro."""
        print("[DashboardView] Botón 'Añadir ítem' presionado.")
        if self.on_add_callback:
            self.on_add_callback(e)