import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
LOGO_PATH = THEME.shield
APP_SUBTITLE = "Ingresa tu clave maestra para desbloquear la bóveda."

INPUT_PASS_LABEL = "Contraseña Maestra"

BTN_PRIMARY_TEXT = "Desbloquear"
BTN_BACK_TEXT = "Volver"

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
ICON_SIZE = 120
SUBTITLE_SIZE = 14
PROMPT_SIZE = 16

CARD_WIDTH = 450
CARD_PADDING = 40
BORDER_RADIUS = 20
INPUT_HEIGHT = 50
SPACING_LARGE = 30
SPACING_SMALL = 10

class LoginView(ft.View):
    def __init__(self, page: ft.Page, on_login=None, on_back=None):
        super().__init__(
            route="/login",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page 
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # Callbacks para conectar con la lógica del Router / Core
        self.on_login = on_login
        self.on_back = on_back
        
        # UI Elements
        self.pass_input = self._build_textfield(INPUT_PASS_LABEL, ft.Icons.LOCK_OUTLINE, is_password=True)
        self.message_text = ft.Text("", visible=False, size=13) # Usado para errores o info

        # Botón Volver (Flotante arriba a la izquierda de la tarjeta)
        self.back_button = ft.TextButton(
            content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text(BTN_BACK_TEXT)]),
            style=ft.ButtonStyle(color=THEME.colors.text_secondary),
            on_click=self.handle_back
        )

        self.controls = [
            ft.Container(
                content=ft.Column([
                    # Botón Volver alineado a la izquierda
                    ft.Row([self.back_button], alignment=ft.MainAxisAlignment.START),
                    # Tarjeta Principal
                    self._build_login_card()
                ], tight=True),
                width=CARD_WIDTH,
                bgcolor=THEME.colors.surface,
                padding=CARD_PADDING,
                border_radius=BORDER_RADIUS,
                shadow=ft.BoxShadow(blur_radius=50, color=ft.Colors.with_opacity(0.3, "black")),
            )
        ]

    def _build_login_card(self):
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=SPACING_LARGE,
            controls=[
                # LOGO AREA
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=SPACING_SMALL,
                    controls=[
                        ft.Image(src=LOGO_PATH, width=ICON_SIZE, height=ICON_SIZE),
                        ft.Text(APP_SUBTITLE, size=SUBTITLE_SIZE, color=THEME.colors.text_secondary, text_align=ft.TextAlign.CENTER),
                    ]
                ),

                # INPUT AREA
                ft.Column(
                    spacing=SPACING_SMALL,
                    controls=[
                        ft.Text(INPUT_PASS_LABEL, size=PROMPT_SIZE, weight="w600", color=THEME.colors.text_main),
                        self.pass_input,
                        self.message_text,
                    ]
                ),

                # ACTION AREA
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=SPACING_SMALL,
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.LOCK_OPEN, size=18), ft.Text(BTN_PRIMARY_TEXT)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            bgcolor=THEME.colors.primary,
                            color="white",
                            height=INPUT_HEIGHT,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=self.handle_login,
                            width=float("inf"),
                        )
                    ]
                )
            ]
        )

    def _build_textfield(self, hint, icon, is_password=False):
        return ft.TextField(
            hint_text=f"Ingresa tu {hint.lower()}",
            prefix_icon=icon,
            password=is_password,
            can_reveal_password=is_password,
            bgcolor=THEME.colors.input_bg if hasattr(THEME.colors, 'input_bg') else ft.Colors.with_opacity(0.05, "white"),
            border_color="transparent",
            focused_border_color=THEME.colors.primary,
            border_radius=10,
            height=INPUT_HEIGHT,
            text_size=14,
            content_padding=15,
            on_submit=self.handle_login # Permite presionar Enter para enviar
        )

    # --- LÓGICA DE INTERACCIÓN ---

    def handle_login(self, e):
        """Valida el campo y llama al controlador externo."""
        password = self.pass_input.value
        if not password:
            self.show_message("Por favor, ingresa tu clave maestra.", is_error=True)
            return
        
        # Si la vista tiene una función asignada, se la pasa
        if self.on_login:
            self.on_login(password)
            
    def handle_back(self, e):
        """Llama al controlador externo para volver."""
        if self.on_back:
            self.on_back()

    def show_message(self, text, is_error=True):
        """Actualiza el texto de error/info en pantalla."""
        self.message_text.value = text
        self.message_text.color = ft.Colors.RED_400 if is_error else THEME.colors.primary
        self.message_text.visible = True
        self.page_ref.update()