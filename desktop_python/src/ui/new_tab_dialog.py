"""
new_tab_dialog.py
─────────────────
Modal-style panel (shown inside the dashboard, not a separate Toplevel)
that lets the user create a custom tab:

  1. Name
  2. Icon  — emoji grid picker
  3. Default fields — dynamic list (label + secret checkbox)
"""

import customtkinter as ctk
import platform
from src.core.vault_schema import ICON_OPTIONS

_EMOJI_FONT_LG = ("Segoe UI Emoji", 22) if platform.system() == "Windows" else ("Roboto", 22)
_EMOJI_FONT    = ("Segoe UI Emoji", 28) if platform.system() == "Windows" else ("Roboto", 28)

_BG       = "#1e1e1e"
_BG2      = "#252525"
_ACCENT   = "#2c8558"
_RED      = "#a33030"
_GREY     = "#888888"
_LABEL_FG = "#aaaaaa"


class NewTabDialog(ctk.CTkFrame):
    """
    Covers the dashboard body area.  on_confirm(name, icon, fields) is called
    with the validated data; on_cancel() dismisses without changes.
    """

    def __init__(self, master, on_confirm, on_cancel):
        super().__init__(master, fg_color=_BG, corner_radius=12)
        self.on_confirm = on_confirm
        self.on_cancel  = on_cancel

        self._selected_icon = ctk.StringVar(value="📁")
        self._field_rows    = []   # list of {"label_entry", "secret_var", "row"}

        # ── Title bar ─────────────────────────────────────────────────────
        title_bar = ctk.CTkFrame(self, fg_color="transparent")
        title_bar.pack(fill="x", padx=18, pady=(16, 8))

        ctk.CTkLabel(
            title_bar, text="Nueva pestaña personalizada",
            font=("Roboto", 17, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            title_bar, text="✕", width=30, height=30,
            fg_color="transparent", hover_color="#333333",
            font=("Roboto", 15),
            command=on_cancel
        ).pack(side="right")

        # ── Scrollable body ───────────────────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=4)

        # 1. Name ──────────────────────────────────────────────────────────
        ctk.CTkLabel(body, text="Nombre *", font=("Roboto", 13, "bold"),
                     anchor="w").pack(anchor="w", pady=(4, 2))

        self._name_entry = ctk.CTkEntry(body, placeholder_text="ej: Criptomonedas",
                                        width=300, height=36)
        self._name_entry.pack(anchor="w", pady=(0, 14))

        # 2. Icon picker ───────────────────────────────────────────────────
        ctk.CTkLabel(body, text="Ícono", font=("Roboto", 13, "bold"),
                     anchor="w").pack(anchor="w", pady=(0, 6))

        # Preview of selected icon
        preview_row = ctk.CTkFrame(body, fg_color="transparent")
        preview_row.pack(anchor="w", pady=(0, 8))

        self._icon_preview = ctk.CTkLabel(
            preview_row,
            textvariable=self._selected_icon,
            font=_EMOJI_FONT
        )
        self._icon_preview.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            preview_row,
            text="← ícono seleccionado",
            font=("Roboto", 12), text_color=_GREY
        ).pack(side="left")

        # Grid of emoji buttons (6 per row)
        grid_frame = ctk.CTkFrame(body, fg_color=_BG2, corner_radius=8)
        grid_frame.pack(fill="x", pady=(0, 16))

        for idx, emoji in enumerate(ICON_OPTIONS):
            col = idx % 6
            row = idx // 6
            btn = ctk.CTkButton(
                grid_frame,
                text=emoji,
                width=44, height=40,
                font=_EMOJI_FONT_LG,
                fg_color="transparent",
                hover_color="#333333",
                command=lambda e=emoji: self._select_icon(e)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)

        # 3. Default fields ────────────────────────────────────────────────
        fields_header = ctk.CTkFrame(body, fg_color="transparent")
        fields_header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            fields_header,
            text="Campos por defecto",
            font=("Roboto", 13, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            fields_header,
            text="(opcionales — definen qué datos tiene cada credencial en esta tab)",
            font=("Roboto", 11), text_color=_GREY
        ).pack(side="left", padx=8)

        # Column headers
        headers = ctk.CTkFrame(body, fg_color="transparent")
        headers.pack(fill="x")
        ctk.CTkLabel(headers, text="Nombre del campo", font=("Roboto", 11),
                     text_color=_LABEL_FG, width=200, anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="¿Secreto?", font=("Roboto", 11),
                     text_color=_LABEL_FG, width=80, anchor="w").pack(side="left")

        # Container for dynamic field rows
        self._fields_container = ctk.CTkFrame(body, fg_color="transparent")
        self._fields_container.pack(fill="x", pady=(2, 6))

        # Start with 2 empty rows
        self._add_field_row()
        self._add_field_row()

        ctk.CTkButton(
            body,
            text="＋ Agregar campo",
            height=30, width=160,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=_GREY,
            hover_color="#2a2a2a",
            command=self._add_field_row
        ).pack(anchor="w", pady=(0, 16))

        # ── Footer ────────────────────────────────────────────────────────
        self._msg = ctk.CTkLabel(self, text="", font=("Roboto", 12))
        self._msg.pack(pady=(0, 6))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(pady=(0, 16))

        ctk.CTkButton(
            footer, text="Crear pestaña",
            width=140, height=38,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._submit
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            footer, text="Cancelar",
            width=100, height=38,
            fg_color="#444444", hover_color="#333333",
            command=on_cancel
        ).pack(side="left")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _select_icon(self, emoji: str):
        self._selected_icon.set(emoji)

    def _add_field_row(self, label: str = "", secret: bool = False):
        row = ctk.CTkFrame(self._fields_container, fg_color="transparent")
        row.pack(fill="x", pady=2)

        label_e = ctk.CTkEntry(row, placeholder_text="ej: Contraseña", width=200)
        label_e.insert(0, label)
        label_e.pack(side="left", padx=(0, 8))

        secret_var = ctk.BooleanVar(value=secret)
        ctk.CTkCheckBox(
            row, text="Secreto", variable=secret_var,
            width=80, font=("Roboto", 12)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row, text="✕", width=26, height=26,
            fg_color=_RED, hover_color="#7a2020",
            command=lambda r=row: self._remove_field_row(r)
        ).pack(side="left")

        entry_info = {"label_entry": label_e, "secret_var": secret_var, "row": row}
        self._field_rows.append(entry_info)

    def _remove_field_row(self, row):
        self._field_rows = [f for f in self._field_rows if f["row"] is not row]
        row.destroy()

    def _submit(self):
        name = self._name_entry.get().strip()
        if not name:
            self._msg.configure(text="El nombre es obligatorio.", text_color="#ff4d4d")
            return

        icon = self._selected_icon.get()

        # Collect non-empty fields
        default_fields = []
        for f in self._field_rows:
            try:
                lbl = f["label_entry"].get().strip()
                sec = f["secret_var"].get()
            except Exception:
                continue
            if lbl:
                default_fields.append({
                    "key":    lbl.lower().replace(" ", "_"),
                    "label":  lbl,
                    "secret": sec,
                })

        self.on_confirm(name, icon, default_fields)