"""
add_credential_panel.py
───────────────────────
Slide-in bottom panel for creating a new credential inside a tab.

Shows:
  - Name field (required)
  - All default_fields of the current tab (optional to fill)
  - "＋ Agregar campo extra" for ad-hoc fields
  - Save / Cancel
"""

import customtkinter as ctk

_BG       = "#222222"
_ACCENT   = "#2c8558"
_GREY     = "#888888"
_LABEL_FG = "#aaaaaa"
_RED      = "#a33030"


class AddCredentialPanel(ctk.CTkFrame):
    """
    Parameters
    ----------
    master      : parent frame (dashboard body)
    tab         : dict — the current tab (provides default_fields)
    on_save     : callable(name, fields, extra_fields)
    on_cancel   : callable()
    """

    def __init__(self, master, tab: dict, on_save, on_cancel):
        super().__init__(master, fg_color=_BG, corner_radius=10)
        self.tab       = tab
        self.on_save   = on_save
        self.on_cancel = on_cancel

        self._entries       = {}    # key → CTkEntry
        self._extra_entries = []    # list of dicts

        # ── Title bar ─────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            title_row,
            text=f"Nueva credencial  {tab['icon']}  {tab['name']}",
            font=("Roboto", 15, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            title_row, text="✕", width=28, height=28,
            fg_color="transparent", hover_color="#333333",
            font=("Roboto", 14),
            command=on_cancel
        ).pack(side="right")

        # ── Scrollable body ───────────────────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color="transparent", height=280)
        body.pack(fill="x", padx=16, pady=4)

        # Name (required)
        self._add_field_row(body, "__name__", "Nombre *", secret=False, required=True)

        # Default fields
        for fd in tab.get("default_fields", []):
            self._add_field_row(body, fd["key"], fd["label"], secret=fd["secret"])

        # Extra fields container
        self._extra_container = ctk.CTkFrame(body, fg_color="transparent")
        self._extra_container.pack(fill="x", pady=(4, 0))

        # ── Footer ────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkButton(
            footer, text="＋ Agregar campo extra",
            height=30, width=180,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=_GREY,
            hover_color="#2a2a2a",
            command=self._add_extra_row
        ).pack(side="left")

        btn_group = ctk.CTkFrame(footer, fg_color="transparent")
        btn_group.pack(side="right")

        ctk.CTkButton(
            btn_group, text="Guardar", width=100, height=34,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._submit
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_group, text="Cancelar", width=90, height=34,
            fg_color="#444444", hover_color="#333333",
            command=on_cancel
        ).pack(side="left")

        self._msg = ctk.CTkLabel(self, text="", font=("Roboto", 11))
        self._msg.pack(pady=(0, 6))

    # ── Helpers ───────────────────────────────────────────────────────────

    def _add_field_row(self, parent, key: str, label: str,
                       secret: bool = False, required: bool = False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        disp = label + (" *" if required else "")
        ctk.CTkLabel(
            row, text=f"{disp}:",
            font=("Roboto", 12), text_color=_LABEL_FG,
            width=170, anchor="w"
        ).pack(side="left")

        entry = ctk.CTkEntry(row, width=230, show="*" if secret else "")
        entry.pack(side="left")
        self._entries[key] = entry

    def _add_extra_row(self, label: str = "", value: str = "", secret: bool = False):
        row = ctk.CTkFrame(self._extra_container, fg_color="transparent")
        row.pack(fill="x", pady=2)

        label_e = ctk.CTkEntry(row, placeholder_text="Nombre del campo", width=130)
        label_e.insert(0, label)
        label_e.pack(side="left", padx=(0, 6))

        value_e = ctk.CTkEntry(row, placeholder_text="Valor", width=150,
                               show="*" if secret else "")
        value_e.insert(0, value)
        value_e.pack(side="left", padx=(0, 6))

        secret_var = ctk.BooleanVar(value=secret)
        ctk.CTkCheckBox(
            row, text="Secreto", variable=secret_var,
            width=70, font=("Roboto", 11)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            row, text="✕", width=26, height=26,
            fg_color=_RED, hover_color="#7a2020",
            command=lambda r=row: r.destroy()
        ).pack(side="left")

        self._extra_entries.append({
            "label_entry": label_e,
            "value_entry": value_e,
            "secret_var":  secret_var,
            "row":         row,
        })

    def _submit(self):
        name = self._entries.get("__name__", None)
        name_val = name.get().strip() if name else ""
        if not name_val:
            self._msg.configure(text="El nombre es obligatorio.", text_color="#ff4d4d")
            return

        fields = {}
        for key, entry in self._entries.items():
            if key != "__name__":
                fields[key] = entry.get()

        extra_fields = []
        for ef in self._extra_entries:
            try:
                lbl = ef["label_entry"].get().strip()
                val = ef["value_entry"].get()
                sec = ef["secret_var"].get()
            except Exception:
                continue
            if lbl:
                extra_fields.append({
                    "key":    lbl.lower().replace(" ", "_"),
                    "label":  lbl,
                    "secret": sec,
                    "value":  val,
                })

        self.on_save(name_val, fields, extra_fields)