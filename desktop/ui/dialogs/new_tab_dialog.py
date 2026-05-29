"""
new_tab_dialog.py
─────────────────
Modal-style panel used inside DashboardView to create custom categories.

Allows:
    • Category name
    • Default fields
    • Secret fields
"""

import re
import customtkinter as ctk
import desktop.ui.themes.theme as theme
from desktop.ui.themes.theme import load_icon

_BG       = theme.c("bg2")
_BG2      = theme.c("card")
_ACCENT   = theme.c("accent")
_RED      = theme.c("danger")
_GREY     = "#888888"
_LABEL_FG = theme.c("text_secondary")


class NewTabDialog(ctk.CTkFrame):

    def __init__(self, master, on_confirm, on_cancel):

        super().__init__(
            master,
            fg_color=_BG,
            corner_radius=12
        )

        self.on_confirm = on_confirm
        self.on_cancel  = on_cancel

        self._field_rows = []

        # Icons
        self._icon_cancel = load_icon("cancel.png", size=(14, 14))
        self._icon_add    = load_icon("add.png", size=(14, 14))

        # ──────────────────────────────────────────────────────────
        # Header
        # ──────────────────────────────────────────────────────────

        title_bar = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        title_bar.pack(
            fill="x",
            padx=18,
            pady=(16, 8)
        )

        ctk.CTkLabel(
            title_bar,
            text="Nueva categoría",
            font=theme.font(17, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            title_bar,
            text="",
            image=self._icon_cancel,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=theme.c("hover"),
            command=self.on_cancel
        ).pack(side="right")

        # ──────────────────────────────────────────────────────────
        # Scroll body
        # ──────────────────────────────────────────────────────────

        body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=4
        )

        # ──────────────────────────────────────────────────────────
        # Name
        # ──────────────────────────────────────────────────────────

        ctk.CTkLabel(
            body,
            text="Nombre *",
            font=theme.font(13, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(4, 2))

        self._name_entry = ctk.CTkEntry(
            body,
            placeholder_text="Ej: Bancos, APIs, Trabajo...",
            width=320,
            height=36
        )

        self._name_entry.pack(
            anchor="w",
            pady=(0, 16)
        )

        # ──────────────────────────────────────────────────────────
        # Fields section
        # ──────────────────────────────────────────────────────────

        fields_header = ctk.CTkFrame(
            body,
            fg_color="transparent"
        )

        fields_header.pack(
            fill="x",
            pady=(0, 6)
        )

        ctk.CTkLabel(
            fields_header,
            text="Campos por defecto",
            font=theme.font(13, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            fields_header,
            text="(opcionales)",
            font=theme.font(11),
            text_color=_GREY
        ).pack(side="left", padx=8)

        # Column headers

        headers = ctk.CTkFrame(
            body,
            fg_color="transparent"
        )

        headers.pack(fill="x")

        ctk.CTkLabel(
            headers,
            text="Campo",
            font=theme.font(11),
            text_color=_LABEL_FG,
            width=220,
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            headers,
            text="Secreto",
            font=theme.font(11),
            text_color=_LABEL_FG,
            width=80,
            anchor="w"
        ).pack(side="left")

        # Dynamic fields container

        self._fields_container = ctk.CTkFrame(
            body,
            fg_color="transparent"
        )

        self._fields_container.pack(
            fill="x",
            pady=(2, 8)
        )

        # Initial field row

        self._add_field_row()

        # Add field button

        ctk.CTkButton(
            body,
            text="Agregar campo",
            image=self._icon_add,
            compound="left",
            height=32,
            width=170,
            fg_color="transparent",
            border_width=1,
            border_color="#444444",
            text_color=_GREY,
            hover_color="#2a2a2a",
            command=self._add_field_row
        ).pack(anchor="w", pady=(0, 18))

        # ──────────────────────────────────────────────────────────
        # Footer
        # ──────────────────────────────────────────────────────────

        self._msg = ctk.CTkLabel(
            self,
            text="",
            font=theme.font(12)
        )

        self._msg.pack(pady=(0, 6))

        footer = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        footer.pack(pady=(0, 16))

        ctk.CTkButton(
            footer,
            text="Crear categoría",
            width=150,
            height=38,
            fg_color=_ACCENT,
            hover_color=theme.c("accent_hover"),
            command=self._submit
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            footer,
            text="Cancelar",
            width=100,
            height=38,
            fg_color="#444444",
            hover_color=theme.c("hover"),
            command=self.on_cancel
        ).pack(side="left")

    # ═════════════════════════════════════════════════════════════
    # FIELD ROWS
    # ═════════════════════════════════════════════════════════════

    def _add_field_row(
        self,
        label: str = "",
        secret: bool = False
    ):

        row = ctk.CTkFrame(
            self._fields_container,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=2
        )

        label_e = ctk.CTkEntry(
            row,
            placeholder_text="Ej: Contraseña",
            width=220
        )

        label_e.insert(0, label)

        label_e.pack(
            side="left",
            padx=(0, 8)
        )

        secret_var = ctk.BooleanVar(value=secret)

        ctk.CTkCheckBox(
            row,
            text="",
            variable=secret_var,
            width=28
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row,
            text="",
            image=self._icon_cancel,
            width=28,
            height=28,
            fg_color=_RED,
            hover_color="#7a2020",
            command=lambda r=row: self._remove_field_row(r)
        ).pack(side="left")

        self._field_rows.append({
            "label_entry": label_e,
            "secret_var":  secret_var,
            "row":         row
        })

    def _remove_field_row(self, row):

        self._field_rows = [
            f for f in self._field_rows
            if f["row"] is not row
        ]

        row.destroy()

    # ═════════════════════════════════════════════════════════════
    # SUBMIT
    # ═════════════════════════════════════════════════════════════

    def _submit(self):

        name = self._name_entry.get().strip()

        if not name:

            self._msg.configure(
                text="El nombre es obligatorio.",
                text_color="#ff4d4d"
            )

            return

        default_fields = []

        for f in self._field_rows:

            try:
                lbl = f["label_entry"].get().strip()
                sec = f["secret_var"].get()

            except Exception:
                continue

            if not lbl:
                continue

            key = re.sub(
                r"[^a-z0-9_]",
                "",
                lbl.lower().replace(" ", "_")
            )

            default_fields.append({
                "key": key,
                "label": lbl,
                "secret": sec,
            })

        self.on_confirm(name, default_fields)