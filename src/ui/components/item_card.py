import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
ICON_FAV = ft.Icons.STAR
ICON_NOT_FAV = ft.Icons.STAR_BORDER
ICON_MORE = ft.Icons.MORE_VERT

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
# Dimensiones y Espaciado
CARD_PADDING = 15
CARD_RADIUS = 12
CARD_SPACING = 15
TEXT_SPACING = 2

# Avatar (Icono/Letra a la izquierda)
AVATAR_SIZE = 40
AVATAR_RADIUS = 8
AVATAR_TEXT_SIZE = 16

# Tamaños de Fuente e Iconos
TITLE_SIZE = 14
SUBTITLE_SIZE = 12
FAV_ICON_SIZE = 20
MORE_ICON_SIZE = 18

# Colores y Opacidades
CARD_BG_OPACITY = 0.02
CARD_BORDER_OPACITY = 0.1
CARD_HOVER_OPACITY = 0.05
FAV_COLOR = "amber"

class ItemCard(ft.Container):
    def __init__(self, title, subtitle, is_fav=False, on_click=None):
        super().__init__(
            padding=CARD_PADDING,
            border_radius=CARD_RADIUS,
            bgcolor=ft.Colors.with_opacity(CARD_BG_OPACITY, "white"),
            border=ft.Border.all(1, ft.Colors.with_opacity(CARD_BORDER_OPACITY, "white")),
            on_click=on_click,
            on_hover=self._handle_hover,
            content=ft.Row(
                spacing=CARD_SPACING,
                controls=[
                    # AVATAR (Contenedor con la inicial)
                    ft.Container(
                        content=ft.Text(
                            title[0].upper() if title else "?", 
                            weight="bold", 
                            size=AVATAR_TEXT_SIZE
                        ),
                        width=AVATAR_SIZE,
                        height=AVATAR_SIZE,
                        bgcolor=THEME.colors.primary,
                        border_radius=AVATAR_RADIUS,
                        alignment=ft.Alignment.CENTER
                    ),
                    
                    # INFORMACIÓN (Título y Subtítulo)
                    ft.Column(
                        expand=True,
                        spacing=TEXT_SPACING,
                        controls=[
                            ft.Text(
                                title, 
                                weight="bold", 
                                size=TITLE_SIZE, 
                                color="white",
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                subtitle, 
                                size=SUBTITLE_SIZE, 
                                color=THEME.colors.text_secondary,
                                overflow=ft.TextOverflow.ELLIPSIS
                            )
                        ]
                    ),
                    
                    # ACCIONES (Favorito y Menú)
                    ft.Icon(
                        icon=ICON_FAV if is_fav else ICON_NOT_FAV,
                        color=FAV_COLOR if is_fav else THEME.colors.text_secondary,
                        size=FAV_ICON_SIZE
                    ),
                    ft.IconButton(
                        icon=ICON_MORE,
                        icon_size=MORE_ICON_SIZE,
                        icon_color=THEME.colors.text_secondary,
                        on_click=lambda _: print(f"Opciones para {title}")
                    )
                ]
            )
        )

    def _handle_hover(self, e):
        """Efecto visual al pasar el mouse por encima de la tarjeta."""
        e.control.bgcolor = (
            ft.Colors.with_opacity(CARD_HOVER_OPACITY, "white") 
            if e.data == "true" 
            else ft.Colors.with_opacity(CARD_BG_OPACITY, "white")
        )
        e.control.update()
        