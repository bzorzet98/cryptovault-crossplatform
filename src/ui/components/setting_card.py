import flet as ft
from src.config import THEME

# ==========================================
# --- UI LAYOUT CONSTANTS ---
# ==========================================
CARD_RADIUS = 12
CARD_PADDING = 20
ICON_CONTAINER_SIZE = 50
ICON_SIZE = 24
TITLE_SIZE = 16
DESC_SIZE = 13

class SettingCard(ft.Container):
    def __init__(self, icon, title, description, action_control):
        super().__init__(
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_radius=CARD_RADIUS,
            padding=CARD_PADDING,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, "white")),
            content=ft.Row([
                # Icono decorativo a la izquierda
                ft.Container(
                    content=ft.Icon(icon, color=THEME.colors.primary, size=ICON_SIZE),
                    width=ICON_CONTAINER_SIZE,
                    height=ICON_CONTAINER_SIZE,
                    bgcolor=ft.Colors.with_opacity(0.1, THEME.colors.primary),
                    border_radius=10,
                ),
                
                # Texto central
                ft.Column([
                    ft.Text(title, size=TITLE_SIZE, weight="bold", color="white"),
                    ft.Text(description, size=DESC_SIZE, color=THEME.colors.text_secondary),
                ], expand=True, spacing=2),
                
                # Control de acción (Switch, Radio, Buttons, etc.)
                ft.Container(content=action_control)
            ], alignment=ft.Alignment.CENTER)
        )