import flet as ft
from src.config import THEME

# ==========================================
# --- RECENT FILE CARD CONSTANTS ---
# ==========================================
RFC_RADIUS = 10
RFC_PADDING = 15
RFC_BG_OPACITY = 0.02
RFC_BORDER_OPACITY = 0.05
RFC_ICON_BOX_SIZE = 48
RFC_ICON_BOX_RADIUS = 8
RFC_ICON_SIZE = 24
RFC_TITLE_SIZE = 14
RFC_PATH_SIZE = 12
RFC_DATE_SIZE = 11
RFC_TEXT_SPACING = 2

# ==========================================
# --- ACTION CARD CONSTANTS ---
# ==========================================
AC_RADIUS = 10
AC_PADDING = 20
AC_ICON_SIZE = 28
AC_ICON_SPACER = 10
AC_TITLE_SIZE = 15
AC_SUBTITLE_SIZE = 12
AC_TEXT_SPACING = 2

class RecentFileCard(ft.Container):
    """Tarjeta para los archivos recientes (columna izquierda)."""
    def __init__(self, icon, title, path, last_seen, on_click=None, on_delete=None):
        super().__init__(
            bgcolor=ft.Colors.with_opacity(RFC_BG_OPACITY, THEME.colors.text_main),
            border_radius=RFC_RADIUS,
            padding=RFC_PADDING,
            border=ft.Border.all(1, ft.Colors.with_opacity(RFC_BORDER_OPACITY, THEME.colors.text_main)),
            on_click=on_click,
            ink=True,
            content=ft.Row([
                # Icono del origen (PC o Nube)
                ft.Container(
                    content=ft.Icon(icon, color=THEME.colors.primary, size=RFC_ICON_SIZE),
                    width=RFC_ICON_BOX_SIZE, height=RFC_ICON_BOX_SIZE,
                    bgcolor=ft.Colors.with_opacity(0.1, THEME.colors.primary),
                    border_radius=RFC_ICON_BOX_RADIUS,
                    alignment=ft.Alignment.CENTER
                ),
                # Información del archivo
                ft.Column([
                    ft.Text(title, size=RFC_TITLE_SIZE, weight="bold", color=THEME.colors.text_main),
                    ft.Text(path, size=RFC_PATH_SIZE, color=THEME.colors.text_secondary),
                    ft.Text(f"Visto por última vez: {last_seen}", size=RFC_DATE_SIZE, color=THEME.colors.text_secondary),
                ], expand=True, spacing=RFC_TEXT_SPACING),
                # Botón de eliminar
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=THEME.colors.text_secondary,
                    on_click=on_delete,
                    tooltip="Quitar de la lista"
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

class ActionCard(ft.Container):
    """Tarjeta para los botones de acción (columna derecha)."""
    def __init__(self, icon, title, subtitle, is_primary=False, on_click=None):
        
        # Colores Dinámicos basados en THEME
        bg_color = THEME.colors.primary if is_primary else ft.Colors.with_opacity(RFC_BG_OPACITY, THEME.colors.text_main)
        border_color = THEME.colors.primary if is_primary else ft.Colors.with_opacity(RFC_BORDER_OPACITY, THEME.colors.text_main)
        icon_color = "white" if is_primary else THEME.colors.text_main
        title_color = "white" if is_primary else THEME.colors.text_main
        subtitle_color = ft.Colors.with_opacity(0.7, "white") if is_primary else THEME.colors.text_secondary

        super().__init__(
            bgcolor=bg_color,
            border_radius=AC_RADIUS,
            padding=AC_PADDING,
            border=ft.Border.all(1, border_color),
            on_click=on_click,
            ink=True,
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=AC_ICON_SIZE),
                ft.Container(width=AC_ICON_SPACER),
                ft.Column([
                    ft.Text(title, size=AC_TITLE_SIZE, weight="bold", color=title_color),
                    ft.Text(subtitle, size=AC_SUBTITLE_SIZE, color=subtitle_color),
                ], spacing=AC_TEXT_SPACING)
            ])
        )