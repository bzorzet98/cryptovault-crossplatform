import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
SEARCH_HINT = "Buscar ítems..."

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
SEARCH_WIDTH = 350
SEARCH_HEIGHT = 45
SEARCH_RADIUS = 10
SEARCH_CONTENT_PADDING = 10
SEARCH_TEXT_SIZE = 14

# Estilo de Bordes
SEARCH_BORDER_COLOR = "transparent"
SEARCH_FOCUSED_BORDER_COLOR = THEME.colors.primary

class SearchBar(ft.TextField):
    def __init__(self, on_change=None):
        super().__init__(
            # Funcionalidad básica
            hint_text=SEARCH_HINT,
            prefix_icon=ft.Icons.SEARCH,
            on_change=on_change,
            
            # Dimensiones
            width=SEARCH_WIDTH,
            height=SEARCH_HEIGHT,
            text_size=SEARCH_TEXT_SIZE,
            content_padding=SEARCH_CONTENT_PADDING,
            
            # Estilo Visual
            bgcolor=THEME.colors.surface,
            border_radius=SEARCH_RADIUS,
            border_color=SEARCH_BORDER_COLOR,
            focused_border_color=SEARCH_FOCUSED_BORDER_COLOR,
            
            # Comportamiento
            can_reveal_password=False, # Aseguramos que sea solo texto
            cursor_color=THEME.colors.primary,
            selection_color=ft.Colors.with_opacity(0.3, THEME.colors.primary),
        )