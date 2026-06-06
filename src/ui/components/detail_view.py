import flet as ft
from src.config import THEME

# ==========================================
# --- 1. APP TEXT & ASSETS CONSTANTS ---
# ==========================================
EMPTY_STATE_TEXT = "Selecciona un elemento para ver los detalles"
LABEL_FAVORITE = "Favorito"
LABEL_CREATED = "Creado"
LABEL_UPDATED = "Última actualización"

# Iconos
ICON_EMPTY_STATE = ft.Icons.CHECK_BOX_OUTLINE_BLANK
ICON_FAV_BORDER = ft.Icons.STAR_BORDER
ICON_COPY = ft.Icons.COPY_ALL_OUTLINED
ICON_VIEW = ft.Icons.VISIBILITY_OUTLINED
ICON_LINK = ft.Icons.OPEN_IN_NEW_OUTLINED

# ==========================================
# --- 2. UI LAYOUT CONSTANTS ---
# ==========================================
# Panel Principal
PANEL_EXPAND = 4
PANEL_RADIUS = 15
PANEL_PADDING = 25

# Cabecera (Header)
HEADER_AVATAR_SIZE = 60
HEADER_AVATAR_RADIUS = 12
HEADER_AVATAR_TEXT_SIZE = 22
HEADER_TITLE_SIZE = 26
HEADER_SPACING = 20

# Campos de Datos (Fields)
FIELD_RADIUS = 10
FIELD_PADDING_V = 12
FIELD_PADDING_H = 15
FIELD_MARGIN_BOTTOM = 10
FIELD_BG_OPACITY = 0.05 # Opacidad sobre el fondo de la superficie

# Tipografía
LABEL_SIZE = 11
VALUE_SIZE = 14
METADATA_SIZE = 11
ACTION_ICON_SIZE = 18

class DetailView(ft.Container):
    def __init__(self):
        super().__init__(
            expand=PANEL_EXPAND,
            bgcolor=THEME.colors.surface,
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
            content=self._build_empty_state()
        )

    def _build_empty_state(self):
        """Estado visual cuando no hay nada seleccionado."""
        return ft.Column(
            [
                ft.Icon(
                    ICON_EMPTY_STATE, 
                    size=50, 
                    color=ft.Colors.with_opacity(0.1, "white")
                ),
                ft.Text(
                    EMPTY_STATE_TEXT, 
                    color=THEME.colors.text_secondary,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def update_details(self, title, username, password, website, notes):
        """Actualiza el panel con la información del ítem seleccionado."""
        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                # HEADER: Avatar + Título + Favorito
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            title[0].upper() if title else "?", 
                            weight="bold", 
                            size=HEADER_AVATAR_TEXT_SIZE
                        ),
                        width=HEADER_AVATAR_SIZE,
                        height=HEADER_AVATAR_SIZE,
                        bgcolor=THEME.colors.primary,
                        border_radius=HEADER_AVATAR_RADIUS,
                        alignment=ft.Alignment.CENTER
                    ),
                    ft.Column([
                        ft.Text(title, size=HEADER_TITLE_SIZE, weight="bold", color="white"),
                        ft.Row([
                            ft.Icon(ICON_FAV_BORDER, size=16, color=THEME.colors.text_secondary),
                            ft.Text(LABEL_FAVORITE, size=12, color=THEME.colors.text_secondary)
                        ], spacing=5)
                    ], expand=True, spacing=2),
                ], spacing=HEADER_SPACING),
                
                ft.Divider(height=40, color=ft.Colors.with_opacity(0.1, "white")),

                # CUERPO: Campos de información
                self._detail_field("Usuario / Email", username, ICON_COPY),
                self._detail_field("Contraseña", "••••••••••••", ICON_VIEW, trailing_icon_2=ICON_COPY),
                self._detail_field("Sitio Web", website, ICON_LINK, is_link=True),
                self._detail_field("Notas", notes, None, multiline=True),
                
                ft.Divider(height=30, color="transparent"),
                
                # FOOTER: Metadatos de fechas
                ft.Column([
                    ft.Text(f"{LABEL_CREATED}: May 20, 2024", size=METADATA_SIZE, color=THEME.colors.text_secondary),
                    ft.Text(f"{LABEL_UPDATED}: May 24, 2024", size=METADATA_SIZE, color=THEME.colors.text_secondary),
                ], spacing=5)
            ]
        )
        self.update()

    def _detail_field(self, label, value, icon, trailing_icon_2=None, is_link=False, multiline=False):
        """Crea un bloque de información con etiqueta, valor y acciones."""
        icons = []
        if icon:
            icons.append(ft.IconButton(icon, icon_size=ACTION_ICON_SIZE, 
                                       icon_color=THEME.colors.text_secondary))
        if trailing_icon_2:
            icons.append(ft.IconButton(trailing_icon_2, icon_size=ACTION_ICON_SIZE, 
                                       icon_color=THEME.colors.text_secondary))

        return ft.Container(
            padding=ft.Padding.symmetric(vertical=FIELD_PADDING_V, horizontal=FIELD_PADDING_H),
            bgcolor=ft.Colors.with_opacity(FIELD_BG_OPACITY, "black"),
            border_radius=FIELD_RADIUS,
            margin=ft.Margin.only(bottom=FIELD_MARGIN_BOTTOM),
            content=ft.Column([
                ft.Text(label, size=LABEL_SIZE, weight="w600", color=THEME.colors.text_secondary),
                ft.Row([
                    ft.Text(
                        value, 
                        expand=True, 
                        size=VALUE_SIZE, 
                        color=THEME.colors.primary if is_link else "white",
                        overflow=ft.TextOverflow.ELLIPSIS,
                        selectable=True # Permite al usuario seleccionar el texto manualmente
                    ),
                    ft.Row(icons, spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=4)
        )
        