import flet as ft
from src.config import THEME

# ==========================================
# --- UI LAYOUT CONSTANTS ---
# ==========================================
DIALOG_WIDTH = 400
DIALOG_RADIUS = 12
DIALOG_PADDING = 30
SPACER_HEIGHT = 20

ICON_SHIELD_SIZE = 30
TITLE_SIZE = 18
SUBTITLE_SIZE = 12

class PasswordDialog(ft.AlertDialog):
    def __init__(self, file_name, on_unlock, on_cancel):
        self.password_field = ft.TextField(
            label="Ingresa tu clave maestra",
            password=True,
            can_reveal_password=True,
            border_color=THEME.colors.primary,
            focused_border_color=THEME.colors.primary,
            prefix_icon=ft.Icons.LOCK_OUTLINE
        )
        
        super().__init__(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=DIALOG_RADIUS),
            content_padding=DIALOG_PADDING,
            content=ft.Container(
                width=DIALOG_WIDTH,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SHIELD, color=THEME.colors.primary, size=ICON_SHIELD_SIZE),
                        ft.Column([
                            ft.Text("Cifrado de Extremo a Extremo", size=SUBTITLE_SIZE, color=THEME.colors.primary),
                            ft.Text(f"Desbloquear {file_name}", size=TITLE_SIZE, weight="bold", color=THEME.colors.text_main),
                        ], spacing=0)
                    ]),
                    ft.Container(height=SPACER_HEIGHT),
                    self.password_field
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=on_cancel),
                ft.ElevatedButton(
                    "Desbloquear", 
                    bgcolor=THEME.colors.primary, 
                    color="white", # Forzamos blanco para contraste con color primario
                    on_click=lambda e: on_unlock(self.password_field.value)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )