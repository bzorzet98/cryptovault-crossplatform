import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
LOGO_PATH = THEME.logo2
APP_TITLE = "CryptoVault"
APP_SUBTITLE = "Tu gestor de contraseñas cifrado."
PROMPT_TEXT = "¿Cómo deseas ingresar?"

BTN_LOCAL_TEXT = "Abrir Bóveda Local"
BTN_DRIVE_TEXT = "Cargar desde Google Drive"
BTN_NEW_TEXT = "Crear Nueva Bóveda"
BTN_SETTINGS_TEXT = "Preferencias"

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
LOGO_SIZE = 380
SUBTITLE_SIZE = 14
PROMPT_SIZE = 16

BTN_WIDTH = 320
BTN_HEIGHT = 45
SPACING_LARGE = 20
SPACING_MEDIUM = 10
SPACING_SMALL = 5

class WelcomeView(ft.View):
    def __init__(self, page: ft.Page, on_load_local=None, 
                 on_load_drive=None, on_create_new=None, 
                 on_settings=None):
        super().__init__(
            route="/welcome",
            bgcolor=THEME.colors.bg,
            padding=0,
        )
        self.page_ref = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

        # --- CALLBACKS ---
        self.on_load_local = on_load_local
        self.on_load_drive = on_load_drive
        self.on_create_new = on_create_new
        self.on_settings = on_settings

        # --- CONTROLES DINÁMICOS ---
        self.status_label = ft.Text("", size=13, visible=False)

        # ==========================================
        # --- INITIALIZE BUTTONS WITH UNIFIED DESIGN ---
        # ==========================================

        # 1. PRIMARY ACCENT BUTTON: Abrir Bóveda Local
        self.btn_local = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=18),
                    ft.Text("Abrir Bóveda Local", size=14, weight="w500")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=THEME.colors.primary,
                color="white",
            ),
            on_click=self._handle_local
        )

        # 2. PRIMARY ACCENT BUTTON: Cargar desde Drive
        self.btn_drive = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CLOUD_OUTLINED, size=18),
                    ft.Text("Cargar desde Google Drive", size=14, weight="w500")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=THEME.colors.primary,
                color="white",
            ),
            on_click=self._handle_drive
        )

        # 3. SECONDARY BUTTON: Crear Nueva Bóveda (Outlined with brand accent color)
        self.btn_new = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=18, color=THEME.colors.primary),
                    ft.Text("Crear Nueva Bóveda", size=14, weight="w500", color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side={"": ft.BorderSide(1, THEME.colors.primary)},  # Subtle brand border
            ),
            on_click=self._handle_new
        )

        # 4. UTILITY BUTTON: Preferencias de la App (Subtle outlined gray)
        self.btn_settings = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=18, color=THEME.colors.text_secondary),
                    ft.Text("Preferencias", size=14, weight="w500", color=THEME.colors.text_secondary)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            width=BTN_WIDTH,
            height=BTN_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side={"": ft.BorderSide(1, "#444444")},  # Sleek dark border matching your theme
            ),
            on_click=self._handle_settings
        )


        # --- ESTRUCTURA DE LA UI ---
        self.controls = [
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    # 1. Branding (Solo la imagen y el subtítulo)
                    ft.Image(src=LOGO_PATH, width=LOGO_SIZE, height=LOGO_SIZE, fit=ft.BoxFit.CONTAIN),
                    # 💡 Se eliminó ft.Text(APP_TITLE) de aquí para evitar la duplicidad
                    ft.Text(APP_SUBTITLE, size=SUBTITLE_SIZE, color=THEME.colors.text_secondary),
                    
                    ft.Container(height=SPACING_LARGE),
                    
                    # 2. Prompt
                    ft.Text(PROMPT_TEXT, size=PROMPT_SIZE, weight="w500", color=THEME.colors.text_main),
                    ft.Container(height=SPACING_SMALL),

                    # 3. Botones de Acción
                    self.btn_local,
                    ft.Container(height=5),
                    self.btn_drive,
                    
                    ft.Container(
                        content=ft.Text("───── o ─────", size=11, 
                                        color=THEME.colors.text_secondary),
                        margin=ft.Margin.symmetric(vertical=15)
                    ),
                    self.btn_new,
                    ft.Container(height=8),
                    self.btn_settings,
                    ft.Container(content=self.status_label, margin=ft.Margin.only(top=15))
                ]
            )
        ]

    # --- MÉTODOS DE INTERFAZ ---

    def show_message(self, text: str, is_error: bool = False):
        """Muestra un mensaje de error o éxito debajo de los botones."""
        self.status_label.value = text
        self.status_label.color = ft.Colors.RED_400 if is_error else THEME.colors.primary
        self.status_label.visible = True
        self.page_ref.update()

    def toggle_loading(self, is_loading: bool):
        """Bloquea los botones y muestra estado de carga."""
        state = is_loading
        
        self.btn_local.disabled = state
        self.btn_drive.disabled = state
        self.btn_new.disabled = state
        self.btn_settings.disabled = state
        
        if is_loading:
            self.status_label.value = "Conectando... por favor espera."
            self.status_label.color = THEME.colors.text_secondary
            self.status_label.visible = True
        else:
            self.status_label.visible = False
            
        self.page_ref.update()

    # --- HANDLERS PRIVADOS ---

    def _handle_local(self, e):
        if self.on_load_local: self.on_load_local()

    def _handle_drive(self, e):
        if self.on_load_drive: self.on_load_drive()

    def _handle_new(self, e):
        if self.on_create_new: self.on_create_new()
        
    def _handle_settings(self, e):
        if self.on_settings: self.on_settings()