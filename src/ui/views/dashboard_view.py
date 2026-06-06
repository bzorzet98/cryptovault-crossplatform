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
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
# Espaciados y Paddings
MAIN_PADDING = 35
TOP_BAR_SPACING = 20
CONTENT_DIVIDER_WIDTH = 20
LIST_COLUMN_EXPAND = 6  # Proporción de la lista vs el detalle

# Tamaños de Fuente e Iconos
TITLE_SIZE = 28
ADD_BTN_RADIUS = 8
SPACER_HEIGHT = 20

class DashboardView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/dashboard",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page
        
        # INSTANCIAR COMPONENTES (Inyectamos la lógica si es necesario)
        self.sidebar = Sidebar()
        self.search_bar = SearchBar(on_change=self.handle_search)
        self.details = DetailView()
        self.items_column = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE, 
            expand=True, 
            spacing=10
        )

        # ESTRUCTURA PRINCIPAL
        self.controls = [
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    # 1. BARRA LATERAL (Fija)
                    self.sidebar,
                    
                    # 2. CONTENIDO PRINCIPAL (Dinámico)
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
                                    tooltip=TOOLTIP_SYNC
                                ),
                                ft.ElevatedButton(
                                    BTN_ADD_TEXT, 
                                    icon=ft.Icons.ADD, 
                                    bgcolor=THEME.colors.primary, 
                                    color="white",
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=ADD_BTN_RADIUS)
                                    )
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            
                            ft.Container(height=SPACER_HEIGHT), 
                            
                            # ÁREA DE TRABAJO (Lista | Detalles)
                            ft.Row([
                                # Columna de la Lista de ítems
                                ft.Column(
                                    [self.items_column], 
                                    expand=LIST_COLUMN_EXPAND
                                ),
                                
                                # Divisor invisible para espaciado consistente
                                ft.VerticalDivider(
                                    width=CONTENT_DIVIDER_WIDTH, 
                                    color="transparent"
                                ),
                                
                                # Panel de Detalles (Componente modular)
                                self.details
                                
                            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
                        ])
                    )
                ]
            )
        ]
        
        # Carga inicial de datos de ejemplo
        self._load_dummy_data()

    def _load_dummy_data(self):
        """Genera datos de prueba para verificar el scroll y el layout."""
        for i in range(1, 15):
            self.items_column.controls.append(
                ItemCard(
                    title=f"Servicio Ejemplo {i}", 
                    subtitle=f"usuario_{i}@mail.com", 
                    is_fav=(i % 4 == 0),
                    on_click=lambda e, n=f"Servicio Ejemplo {i}": self.on_item_selected(n)
                )
            )

    def on_item_selected(self, name):
        """Lógica de comunicación entre la lista y el panel de detalles."""
        # En una app real, aquí buscaríamos los datos en el JsonManager
        self.details.update_details(
            title=name,
            username="admin_user",
            password="secure_password_123",
            website="https://app.pro.com",
            notes="Esta es una nota generada automáticamente para el componente de prueba."
        )

    def handle_search(self, e):
        """Manejador del evento de búsqueda."""
        # Aquí se filtraría la lista de items_column.controls
        print(f"Buscando: {e.data}")