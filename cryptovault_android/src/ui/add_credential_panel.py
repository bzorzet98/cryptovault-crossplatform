"""
add_credential_panel.py
───────────────────────
Slide-in panel for creating a new credential inside a tab.
Includes an integrated password generator for secret fields.
"""

import customtkinter as ctk
from src.ui.password_generator import PasswordGeneratorWidget

_BG       = "#222222"
_ACCENT   = "#2c8558"
_GREY     = "#888888"
_LABEL_FG = "#aaaaaa"
_RED      = "#a33030"


class AddCredentialPanel(ctk.CTkFrame):
    def __init__(self, master, tab: dict, on_save, on_cancel):
        super().__init__(master, fg_color=_BG, corner_radius=10)
        self.tab       = tab
        self.on_save   = on_save
        self.on_cancel = on_cancel

        self._entries        = {}
        self._extra_entries  = []
        self._gen_widget     = None

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
            command=on_cancel
        ).pack(side="right")

        # ── Scrollable body ───────────────────────────────────────────────
        self._body = ctk.CTkScrollableFrame(self, fg_color="transparent", height=260)
        self._body.pack(fill="x", padx=16, pady=4)

        self._add_field_row(self._body, "__name__", "Nombre", secret=False, required=True)

        for fd in tab.get("default_fields", []):
            self._add_field_row(self._body, fd["key"], fd["label"], secret=fd["secret"])

        self._extra_container = ctk.CTkFrame(self._body, fg_color="transparent")
        self._extra_container.pack(fill="x", pady=(4, 0))

        # ── Generator placeholder (injected here when active) ─────────────
        self._gen_anchor = ctk.CTkFrame(self, fg_color="transparent", height=1)
        self._gen_anchor.pack(fill="x")

        # ── Footer ────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(4, 6))

        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkButton(
            left, text="＋ Campo extra",
            height=30, width=130,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=_GREY,
            hover_color="#2a2a2a",
            command=self._add_extra_row
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            left, text="🔑 Generar",
            height=30, width=100,
            fg_color="transparent", border_width=1,
            border_color="#2c6040", text_color="#2c8558",
            hover_color="#1a2a20",
            command=self._toggle_generator
        ).pack(side="left")

        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(
            right, text="Guardar", width=100, height=34,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._submit
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right, text="Cancelar", width=90, height=34,
            fg_color="#444444", hover_color="#333333",
            command=on_cancel
        ).pack(side="left")

        self._msg = ctk.CTkLabel(self, text="", font=("Roboto", 11))
        self._msg.pack(pady=(0, 6))

    # ── Field rows ────────────────────────────────────────────────────────

    def _add_field_row(self, parent, key, label, secret=False, required=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        ctk.CTkLabel(
            row, text=f"{label}{' *' if required else ''}:",
            font=("Roboto", 12), text_color=_LABEL_FG,
            width=160, anchor="w"
        ).pack(side="left")

        entry = ctk.CTkEntry(row, width=200, show="*" if secret else "")
        entry.pack(side="left", padx=(0, 6))
        self._entries[key] = entry

        if secret:
            _vis = {"on": False}
            def _toggle(e=entry, v=_vis):
                v["on"] = not v["on"]
                e.configure(show="" if v["on"] else "*")
            ctk.CTkButton(
                row, text="👁", width=28, height=28,
                fg_color="#333333", hover_color="#444444",
                command=_toggle
            ).pack(side="left")

    def _add_extra_row(self, label="", value="", secret=False):
        row = ctk.CTkFrame(self._extra_container, fg_color="transparent")
        row.pack(fill="x", pady=2)

        label_e = ctk.CTkEntry(row, placeholder_text="Nombre del campo", width=120)
        label_e.insert(0, label)
        label_e.pack(side="left", padx=(0, 6))

        value_e = ctk.CTkEntry(row, placeholder_text="Valor", width=140,
                               show="*" if secret else "")
        value_e.insert(0, value)
        value_e.pack(side="left", padx=(0, 6))

        secret_var = ctk.BooleanVar(value=secret)
        ctk.CTkCheckBox(row, text="Secreto", variable=secret_var,
                        width=70, font=("Roboto", 11)).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            row, text="✕", width=26, height=26,
            fg_color=_RED, hover_color="#7a2020",
            command=lambda r=row: r.destroy()
        ).pack(side="left")

        self._extra_entries.append({
            "label_entry": label_e, "value_entry": value_e,
            "secret_var": secret_var, "row": row,
        })

    # ── Password generator ────────────────────────────────────────────────

    def _toggle_generator(self):
        if self._gen_widget and self._gen_widget.winfo_exists():
            self._gen_widget.destroy()
            self._gen_widget = None
            return

        # Target: first secret field
        target_key = next(
            (k for k, e in self._entries.items()
             if k != "__name__" and e.cget("show") == "*"),
            None
        )

        self._gen_widget = PasswordGeneratorWidget(
            master=self._gen_anchor,
            on_use=lambda pw: self._apply_generated(pw, target_key)
        )
        self._gen_widget.pack(fill="x", padx=16, pady=(4, 0))

    def _apply_generated(self, pw, key):
        if key and key in self._entries:
            e = self._entries[key]
            e.delete(0, "end")
            e.insert(0, pw)
        if self._gen_widget and self._gen_widget.winfo_exists():
            self._gen_widget.destroy()
            self._gen_widget = None

    # ── Submit ────────────────────────────────────────────────────────────

    def _submit(self):
        name_e   = self._entries.get("__name__")
        name_val = name_e.get().strip() if name_e else ""
        if not name_val:
            self._msg.configure(text="El nombre es obligatorio.", text_color=_RED)
            return

        fields = {k: e.get() for k, e in self._entries.items() if k != "__name__"}

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
                    "key": lbl.lower().replace(" ", "_"),
                    "label": lbl, "secret": sec, "value": val,
                })

        self.on_save(name_val, fields, extra_fields)