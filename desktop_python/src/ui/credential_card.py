"""
credential_card.py
──────────────────
A single credential displayed as a collapsible card inside a tab.

Collapsed:  name + preview of first non-secret field  + [👁 Ver] [✏] [🗑]
Expanded:   all fields with individual show/hide + copy
Edit mode:  inline inputs for every field, extra fields editable, save/cancel
"""

import customtkinter as ctk

_BG       = "#252525"
_BG_FIELD = "#1e1e1e"
_ACCENT   = "#2c8558"
_RED      = "#a33030"
_GREY     = "#888888"
_LABEL_FG = "#aaaaaa"


class CredentialCard(ctk.CTkFrame):
    """
    Parameters
    ----------
    master      : parent scrollable frame
    credential  : dict  (from vault_schema)
    tab         : dict  (owner tab — provides default_fields)
    on_save     : callable(updated_credential)
    on_delete   : callable(credential_id)
    read_only   : bool
    """

    def __init__(self, master, credential: dict, tab: dict,
                 on_save, on_delete, read_only: bool = False):
        super().__init__(master, fg_color=_BG, corner_radius=10)
        self.pack(fill="x", pady=5, padx=2)

        self.credential = credential
        self.tab        = tab
        self.on_save    = on_save
        self.on_delete  = on_delete
        self.read_only  = read_only

        self._expanded  = False
        self._edit_mode = False

        # Collapsed row — always visible
        self._collapsed = ctk.CTkFrame(self, fg_color="transparent")
        self._collapsed.pack(fill="x", padx=12, pady=10)
        self._render_collapsed()

        # Expanded panel — hidden by default, created once
        self._expanded_panel = ctk.CTkFrame(self, fg_color=_BG_FIELD, corner_radius=6)
        self._render_expanded()

        # Edit panel — hidden by default, rebuilt on demand
        self._edit_panel = ctk.CTkFrame(self, fg_color=_BG_FIELD, corner_radius=6)

    # ══════════════════════════════════════════════════════════════════════
    # COLLAPSED ROW
    # ══════════════════════════════════════════════════════════════════════

    def _render_collapsed(self):
        """(Re)populate self._collapsed without touching its pack geometry."""
        for w in self._collapsed.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._collapsed,
            text=self.credential["name"],
            font=("Roboto", 14, "bold"), anchor="w"
        ).pack(side="left")

        preview = self._get_preview()
        if preview:
            ctk.CTkLabel(
                self._collapsed,
                text=f"  ·  {preview}",
                font=("Roboto", 12), text_color=_GREY, anchor="w"
            ).pack(side="left")

        btn_frame = ctk.CTkFrame(self._collapsed, fg_color="transparent")
        btn_frame.pack(side="right")

        self._btn_expand = ctk.CTkButton(
            btn_frame, text="👁 Ver", width=60, height=28,
            fg_color="#333333", hover_color="#3f3f3f",
            font=("Roboto", 12),
            command=self._toggle_expand
        )
        self._btn_expand.pack(side="left", padx=(0, 6))

        if not self.read_only:
            ctk.CTkButton(
                btn_frame, text="✏", width=32, height=28,
                fg_color="#333333", hover_color="#3f3f3f",
                font=("Roboto", 14),
                command=self._enter_edit_mode
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                btn_frame, text="🗑", width=32, height=28,
                fg_color=_RED, hover_color="#7a2020",
                font=("Roboto", 14),
                command=lambda: self.on_delete(self.credential["id"])
            ).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════
    # EXPANDED PANEL  (view mode)
    # ══════════════════════════════════════════════════════════════════════

    def _render_expanded(self):
        """(Re)populate self._expanded_panel without touching its pack geometry."""
        for w in self._expanded_panel.winfo_children():
            w.destroy()

        self._field_rows = {}  # key → {var, visible, value, secret}

        for fd in self._all_field_defs():
            key    = fd["key"]
            label  = fd["label"]
            secret = fd["secret"]
            value  = self._get_value(key)

            row = ctk.CTkFrame(self._expanded_panel, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=3)

            ctk.CTkLabel(
                row, text=f"{label}:",
                font=("Roboto", 12), text_color=_LABEL_FG,
                width=170, anchor="w"
            ).pack(side="left")

            display_var = ctk.StringVar(value=("••••••••" if secret else value))
            ctk.CTkLabel(
                row, textvariable=display_var,
                font=("Roboto", 12), anchor="w"
            ).pack(side="left", fill="x", expand=True)

            self._field_rows[key] = {
                "var": display_var, "visible": not secret,
                "value": value, "secret": secret
            }

            # Copy
            ctk.CTkButton(
                row, text="⎘", width=28, height=24,
                fg_color="#333333", hover_color="#3f3f3f",
                command=lambda v=value: self._copy(v)
            ).pack(side="right", padx=(4, 0))

            # Show/hide (only secret fields)
            if secret:
                ctk.CTkButton(
                    row, text="👁", width=28, height=24,
                    fg_color="#333333", hover_color="#3f3f3f",
                    command=lambda k=key: self._toggle_visibility(k)
                ).pack(side="right", padx=(4, 0))

        ctk.CTkFrame(self._expanded_panel, fg_color="transparent", height=8).pack()

    # ══════════════════════════════════════════════════════════════════════
    # EDIT PANEL
    # ══════════════════════════════════════════════════════════════════════

    def _render_edit(self):
        """Rebuild all widgets inside self._edit_panel."""
        for w in self._edit_panel.winfo_children():
            w.destroy()

        self._edit_entries  = {}   # key → CTkEntry
        self._extra_entries = []   # list of dicts

        # Name
        self._add_edit_row(self._edit_panel, "__name__", "Nombre",
                           value=self.credential["name"], secret=False)

        # Default fields
        for fd in self._all_field_defs():
            self._add_edit_row(
                self._edit_panel, fd["key"], fd["label"],
                value=self._get_value(fd["key"]), secret=fd["secret"]
            )

        # Extra fields container
        self._extra_edit_container = ctk.CTkFrame(self._edit_panel, fg_color="transparent")
        self._extra_edit_container.pack(fill="x", padx=14)

        for ef in self.credential.get("extra_fields", []):
            self._add_extra_row(ef["label"], ef["value"], ef["secret"])

        # + Add extra field
        ctk.CTkButton(
            self._edit_panel, text="＋ Agregar campo extra",
            height=28, width=180,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=_GREY, hover_color="#2a2a2a",
            command=lambda: self._add_extra_row()
        ).pack(anchor="w", padx=14, pady=(6, 4))

        # Save / Cancel
        btn_row = ctk.CTkFrame(self._edit_panel, fg_color="transparent")
        btn_row.pack(anchor="e", padx=14, pady=(4, 10))

        ctk.CTkButton(
            btn_row, text="Guardar", width=90,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._save_edit
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Cancelar", width=80,
            fg_color="#444444", hover_color="#333333",
            command=self._cancel_edit
        ).pack(side="left")

    def _add_edit_row(self, parent, key: str, label: str,
                      value: str = "", secret: bool = False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=3)

        ctk.CTkLabel(
            row, text=f"{label}:",
            font=("Roboto", 12), text_color=_LABEL_FG,
            width=150, anchor="w"
        ).pack(side="left")

        entry = ctk.CTkEntry(row, width=220, show="*" if secret else "")
        entry.insert(0, value)
        entry.pack(side="left")
        self._edit_entries[key] = entry

    def _add_extra_row(self, label: str = "", value: str = "", secret: bool = False):
        row = ctk.CTkFrame(self._extra_edit_container, fg_color="transparent")
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

    # ══════════════════════════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_expand(self):
        if self._edit_mode:
            return
        self._expanded = not self._expanded
        if self._expanded:
            self._expanded_panel.pack(fill="x", padx=10, pady=(0, 10))
            self._btn_expand.configure(text="▲ Ocultar")
        else:
            self._expanded_panel.pack_forget()
            self._btn_expand.configure(text="👁 Ver")

    def _toggle_visibility(self, key: str):
        info = self._field_rows.get(key)
        if not info:
            return
        info["visible"] = not info["visible"]
        info["var"].set(info["value"] if info["visible"] else "••••••••")

    def _enter_edit_mode(self):
        self._edit_mode = True
        # Collapse view panel if open
        self._expanded_panel.pack_forget()
        self._expanded = False
        self._btn_expand.configure(text="👁 Ver")
        # Rebuild and show edit panel
        self._render_edit()
        self._edit_panel.pack(fill="x", padx=10, pady=(0, 10))

    def _cancel_edit(self):
        self._edit_mode = False
        self._edit_panel.pack_forget()

    def _save_edit(self):
        name_val = self._edit_entries.get("__name__")
        name_val = name_val.get().strip() if name_val else ""
        if not name_val:
            return

        # Collect standard fields
        new_fields = {}
        for key, entry in self._edit_entries.items():
            if key != "__name__":
                new_fields[key] = entry.get()

        # Collect extra fields (skip rows that were destroyed with ✕)
        new_extras = []
        for ef in self._extra_entries:
            try:
                lbl = ef["label_entry"].get().strip()
                val = ef["value_entry"].get()
                sec = ef["secret_var"].get()
            except Exception:
                continue
            if lbl:
                new_extras.append({
                    "key":    lbl.lower().replace(" ", "_"),
                    "label":  lbl,
                    "secret": sec,
                    "value":  val,
                })

        # Mutate credential in place
        self.credential["name"]         = name_val
        self.credential["fields"]       = new_fields
        self.credential["extra_fields"] = new_extras

        # Refresh both panels with new data (geometry untouched)
        self._render_collapsed()
        self._render_expanded()

        self._edit_mode = False
        self._edit_panel.pack_forget()

        self.on_save(self.credential)

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _all_field_defs(self) -> list:
        """default_fields from tab only — extra_fields are handled separately."""
        return list(self.tab.get("default_fields", []))

    def _get_value(self, key: str) -> str:
        return self.credential.get("fields", {}).get(key, "")

    def _get_preview(self) -> str:
        for fd in self.tab.get("default_fields", []):
            if not fd["secret"]:
                v = self.credential.get("fields", {}).get(fd["key"], "")
                if v:
                    return v
        return ""

    def _copy(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)