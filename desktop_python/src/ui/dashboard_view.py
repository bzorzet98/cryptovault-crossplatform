"""
dashboard_view.py
─────────────────
Main vault view. Replaces the flat list with a tabbed interface.

Layout:
    ┌─────────────────────────────────────────────────────────┐
    │  🗄 vault_name        ● Local/Sync   ← Menú   🔒 Cerrar │  header
    ├─────────────────────────────────────────────────────────┤
    │  [🏦 Bancos] [📧 Emails] … [🗑️] [＋]   [📤] [🔄 Sync]  │  tab bar
    ├─────────────────────────────────────────────────────────┤
    │  (status message)                                       │
    ├─────────────────────────────────────────────────────────┤
    │  scrollable CredentialCards for active tab              │
    ├─────────────────────────────────────────────────────────┤
    │  [＋ Agregar …]                    [Solo Lectura switch] │  footer
    └─────────────────────────────────────────────────────────┘
"""

import customtkinter as ctk
from src.core.vault_schema import DELETED_TAB_ID, purge_old_deleted, get_tab
from src.ui.credential_card import CredentialCard
from src.ui.add_credential_panel import AddCredentialPanel
from src.ui.new_tab_dialog import NewTabDialog

_ACCENT     = "#2c8558"
_RED        = "#a33030"
_GREY       = "#888888"
_TAB_ON     = "#2c8558"
_TAB_OFF    = "#2a2a2a"

import platform
# On Windows use Segoe UI Emoji; on macOS/Linux fall back to system emoji font
_EMOJI_FONT = ("Segoe UI Emoji", 12) if platform.system() == "Windows" else ("Roboto", 12)
_EMOJI_FONT_LG = ("Segoe UI Emoji", 16) if platform.system() == "Windows" else ("Roboto", 16)


class DashboardView(ctk.CTkFrame):

    def __init__(self, master, controller, data: dict):
        super().__init__(master)
        self.controller       = controller
        self.vault_data       = data
        self._active_tab_id   = None
        self._tab_buttons     = {}
        self._add_panel       = None
        self._new_tab_dialog  = None
        self._btn_sync        = None
        self._btn_del_tab     = None

        # Purge old deleted credentials silently on open
        if purge_old_deleted(self.vault_data):
            self._persist_silent()

        self._build_header()
        self._build_tab_bar()
        self._build_status_bar()
        self._build_body()
        self._build_footer()

        # Select first non-deleted tab
        first = next(
            (t for t in self.vault_data.get("tabs", []) if t["id"] != DELETED_TAB_ID),
            None
        )
        if first:
            self._switch_tab(first["id"])

    # ══════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 4))

        vault_name = self.controller.storage.get_name_without_extension()
        self._title_label = ctk.CTkLabel(
            header, text=f"🗄  {vault_name}",
            font=("Roboto", 18, "bold"), cursor="hand2"
        )
        self._title_label.pack(side="left")
        self._title_label.bind("<Button-1>", lambda e: self._show_rename_form())

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        is_sync      = getattr(self.controller, 'drive_source', False)
        status_color = _ACCENT if is_sync else _GREY
        status_text  = "● Sincronizado" if is_sync else "● Local"

        self._status_indicator = ctk.CTkLabel(
            right, text=status_text,
            text_color=status_color, font=("Roboto", 12)
        )
        self._status_indicator.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            right, text="← Menú", width=72, height=30,
            fg_color="transparent", border_width=1,
            border_color="#555555", text_color="#aaaaaa", hover_color="#333333",
            command=lambda: self.controller.handle_exit(then_quit=False)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            right, text="🔒 Cerrar", width=80, height=30,
            fg_color="#444444",
            command=lambda: self.controller.handle_exit(then_quit=True)
        ).pack(side="left")

        # ── Rename form (hidden) ──────────────────────────────────────────
        self._rename_frame = ctk.CTkFrame(self, fg_color="#222222", corner_radius=8)
        ri = ctk.CTkFrame(self._rename_frame, fg_color="transparent")
        ri.pack(padx=14, pady=10, fill="x")
        ctk.CTkLabel(ri, text="Nuevo nombre:", font=("Roboto", 12),
                     text_color="#aaaaaa").pack(anchor="w")
        row = ctk.CTkFrame(ri, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        self._rename_entry = ctk.CTkEntry(row, placeholder_text="nombre_boveda", width=200)
        self._rename_entry.pack(side="left", padx=(0, 6))
        self._rename_entry.bind("<Return>", lambda e: self._submit_rename())
        ctk.CTkLabel(row, text=".data", font=("Roboto", 12),
                     text_color="#666666").pack(side="left")
        btn_row = ctk.CTkFrame(ri, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(8, 0))
        ctk.CTkButton(btn_row, text="Renombrar", width=110,
                      command=self._submit_rename).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancelar", width=80,
                      fg_color="#444444", hover_color="#333333",
                      command=self._hide_rename_form).pack(side="left")
        self._rename_msg = ctk.CTkLabel(ri, text="", font=("Roboto", 11))
        self._rename_msg.pack(anchor="w", pady=(4, 0))

    def _build_tab_bar(self):
        bar_outer = ctk.CTkFrame(self, fg_color="#1a1a1a", height=54)
        bar_outer.pack(fill="x")
        bar_outer.pack_propagate(False)

        self._tab_bar_inner = ctk.CTkScrollableFrame(
            bar_outer, orientation="horizontal",
            fg_color="transparent", height=48,
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#444444"
        )
        self._tab_bar_inner.pack(fill="both", expand=True, padx=4)

        self._rebuild_tab_bar()

    def _rebuild_tab_bar(self):
        for w in self._tab_bar_inner.winfo_children():
            w.destroy()
        self._tab_buttons = {}
        self._btn_sync    = None

        for tab in self.vault_data.get("tabs", []):
            self._add_tab_button(tab)

        # ＋ new tab
        ctk.CTkButton(
            self._tab_bar_inner,
            text="＋", width=34, height=32,
            fg_color="transparent", border_width=1,
            border_color="#444444", text_color=_GREY,
            hover_color="#2a2a2a", font=_EMOJI_FONT_LG,
            command=self._show_new_tab_dialog
        ).pack(side="left", padx=(4, 2), pady=7)

        # Action buttons pinned right
        actions = ctk.CTkFrame(self._tab_bar_inner, fg_color="transparent")
        actions.pack(side="right", padx=8, pady=7)

        ctk.CTkButton(
            actions, text="📤", width=34, height=32,
            fg_color="transparent", hover_color="#333333",
            font=_EMOJI_FONT_LG,
            command=self.controller.handle_export_vault
        ).pack(side="left", padx=(0, 4))

        if not getattr(self.controller, 'drive_source', False):
            self._btn_sync = ctk.CTkButton(
                actions, text="🔄 Sync",
                width=80, height=32,
                fg_color=_ACCENT, hover_color="#1e5c3d",
                font=("Roboto", 12),
                command=lambda: self.controller.handle_sync_drive(then_quit=False)
            )
            self._btn_sync.pack(side="left")

    def _add_tab_button(self, tab: dict):
        count = len(tab.get("credentials", []))
        label = f"{tab['icon']}  {tab['name']}  ({count})"
        btn = ctk.CTkButton(
            self._tab_bar_inner,
            text=label,
            height=32,
            fg_color=_TAB_OFF, hover_color="#383838",
            text_color="#cccccc", font=("Segoe UI Emoji", 12),
            corner_radius=6,
            command=lambda tid=tab["id"]: self._switch_tab(tid)
        )
        btn.pack(side="left", padx=(4, 2), pady=7)
        self._tab_buttons[tab["id"]] = btn

    def _build_status_bar(self):
        self._msg_label = ctk.CTkLabel(self, text="", font=("Roboto", 12))
        self._msg_label.pack(pady=(4, 0))

    def _build_body(self):
        # ── Search bar ────────────────────────────────────────────────────
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(4, 0))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_search_change())

        ctk.CTkEntry(
            search_row,
            textvariable=self._search_var,
            placeholder_text="🔍  Buscar credencial...",
            height=32
        ).pack(fill="x")

        # ── Scroll body ───────────────────────────────────────────────────
        self._body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._body.pack(fill="both", expand=True, padx=16, pady=(4, 0))

    def _on_search_change(self):
        """Re-render active tab filtered by search query."""
        tab = self._active_tab()
        if tab:
            self._render_tab(tab)

    def _build_footer(self):
        self._footer = ctk.CTkFrame(self, fg_color="transparent")
        self._footer.pack(fill="x", padx=16, pady=8)

        self._btn_add = ctk.CTkButton(
            self._footer, text="＋ Agregar credencial",
            height=36, fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._show_add_panel
        )
        self._btn_add.pack(side="left")

        self._readonly_switch = ctk.CTkSwitch(
            self._footer, text="Solo Lectura",
            command=self._toggle_readonly, width=100
        )
        self._readonly_switch.pack(side="right")
        if getattr(self.controller, 'read_only', False):
            self._readonly_switch.select()
            self._apply_readonly(True)

    # ══════════════════════════════════════════════════════════════════════
    # TAB SWITCHING & RENDERING
    # ══════════════════════════════════════════════════════════════════════

    def _switch_tab(self, tab_id: str):
        self._dismiss_add_panel()
        self._dismiss_new_tab_dialog()

        self._active_tab_id = tab_id
        for tid, btn in self._tab_buttons.items():
            btn.configure(fg_color=_TAB_ON if tid == tab_id else _TAB_OFF)

        tab = next(
            (t for t in self.vault_data.get("tabs", []) if t["id"] == tab_id), None
        )
        if tab:
            self._render_tab(tab)
            self._refresh_footer(tab)

    def _render_tab(self, tab: dict):
        # Destroy credential cards but not the add panel (if open)
        for w in self._body.winfo_children():
            if w is not self._add_panel:
                w.destroy()

        credentials = tab.get("credentials", [])
        query = self._search_var.get().strip().lower()
        if query:
            credentials = [c for c in credentials if query in c["name"].lower()]
        is_del      = (tab["id"] == DELETED_TAB_ID)
        is_ro       = getattr(self.controller, 'read_only', False)

        if not credentials:
            ctk.CTkLabel(
                self._body,
                text="No hay credenciales aquí todavía.",
                text_color=_GREY, font=("Roboto", 13)
            ).pack(pady=30)
            return

        for cred in credentials:
            if is_del:
                self._build_deleted_card(cred)
            else:
                CredentialCard(
                    master=self._body,
                    credential=cred,
                    tab=tab,
                    on_save=lambda c, tid=tab["id"]: self._on_credential_updated(tid, c),
                    on_delete=lambda cid, tid=tab["id"]: self._on_credential_deleted(tid, cid),
                    verify_master=lambda pw: pw == self.controller.master_key,
                    on_copy=self.controller.schedule_clipboard_clear,
                    read_only=is_ro
                )

    def _build_deleted_card(self, cred: dict):
        card = ctk.CTkFrame(self._body, fg_color="#252525", corner_radius=10)
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            inner, text=cred["name"],
            font=("Roboto", 14, "bold"), anchor="w"
        ).pack(side="left")

        deleted_at = cred.get("deleted_at", "")
        if deleted_at:
            ctk.CTkLabel(
                inner, text=f"  eliminado: {deleted_at[:10]}",
                font=("Roboto", 11), text_color=_GREY
            ).pack(side="left")

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame, text="↩ Restaurar", width=90, height=28,
            fg_color="#2a4a3a", hover_color="#1e5c3d",
            font=("Roboto", 12),
            command=lambda c=cred: self._show_restore_picker(c)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_frame, text="🗑 Borrar", width=80, height=28,
            fg_color=_RED, hover_color="#7a2020",
            font=("Roboto", 12),
            command=lambda c=cred: self._on_purge_credential(c)
        ).pack(side="left")

    def _show_restore_picker(self, cred: dict):
        picker = ctk.CTkToplevel(self)
        picker.title("Restaurar a…")
        picker.geometry("280x340")
        picker.grab_set()

        ctk.CTkLabel(picker, text="¿A qué pestaña restaurar?",
                     font=("Roboto", 14, "bold")).pack(pady=(16, 10))

        frame = ctk.CTkScrollableFrame(picker, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=12)

        for tab in self.vault_data.get("tabs", []):
            if tab["id"] == DELETED_TAB_ID:
                continue
            ctk.CTkButton(
                frame,
                text=f"{tab['icon']}  {tab['name']}",
                height=36, fg_color="#2a2a2a", hover_color="#333333",
                anchor="w",
                command=lambda tid=tab["id"]: self._do_restore(cred, tid, picker)
            ).pack(fill="x", pady=3)

        ctk.CTkButton(picker, text="Cancelar", fg_color="#444444",
                      command=picker.destroy).pack(pady=10)

    def _do_restore(self, cred: dict, target_tab_id: str, picker):
        picker.destroy()
        self.controller.handle_restore_credential(cred["id"], target_tab_id)
        self.vault_data = self.controller._last_decrypted_data
        self._switch_tab(DELETED_TAB_ID)

    def _refresh_footer(self, tab: dict):
        is_del = (tab["id"] == DELETED_TAB_ID)
        is_ro  = getattr(self.controller, 'read_only', False)

        if is_del or is_ro:
            self._btn_add.pack_forget()
        else:
            self._btn_add.pack(side="left")
            self._btn_add.configure(text=f"＋ Agregar en {tab['name']}")

        # Remove previous delete-tab button if any
        if self._btn_del_tab:
            self._btn_del_tab.pack_forget()
            self._btn_del_tab = None

        if not tab.get("is_system", True) and not is_ro:
            self._btn_del_tab = ctk.CTkButton(
                self._footer,
                text="🗑 Eliminar pestaña",
                height=36, width=150,
                fg_color=_RED, hover_color="#7a2020",
                command=lambda tid=tab["id"]: self._on_delete_tab(tid)
            )
            self._btn_del_tab.pack(side="left", padx=(10, 0))

    # ══════════════════════════════════════════════════════════════════════
    # ADD CREDENTIAL
    # ══════════════════════════════════════════════════════════════════════

    def _show_add_panel(self):
        if getattr(self.controller, 'read_only', False):
            return
        self._dismiss_new_tab_dialog()

        tab = self._active_tab()
        if not tab or tab["id"] == DELETED_TAB_ID:
            return

        if self._add_panel:
            self._dismiss_add_panel()
            return

        self._add_panel = AddCredentialPanel(
            master=self._body,   # inside the scroll area, always visible
            tab=tab,
            on_save=self._on_credential_added,
            on_cancel=self._dismiss_add_panel
        )
        # Insert at the TOP of the scroll frame so it's immediately visible
        self._add_panel.pack(fill="x", padx=4, pady=(0, 8))
        self._add_panel.lift()

    def _dismiss_add_panel(self):
        if self._add_panel:
            self._add_panel.destroy()
            self._add_panel = None

    def _on_credential_added(self, name: str, fields: dict, extra_fields: list):
        tab = self._active_tab()
        if not tab:
            return
        self.controller.handle_add_credential(tab["id"], name, fields, extra_fields)
        self.vault_data = self.controller._last_decrypted_data
        self._dismiss_add_panel()
        self._switch_tab(tab["id"])
        self.show_message("Credencial guardada.", "success")

    # ══════════════════════════════════════════════════════════════════════
    # CREDENTIAL UPDATE / DELETE / PURGE
    # ══════════════════════════════════════════════════════════════════════

    def _on_credential_updated(self, tab_id: str, updated_cred: dict):
        self.controller.handle_update_credential(tab_id, updated_cred)
        self.vault_data = self.controller._last_decrypted_data
        self.show_message("Cambios guardados.", "success")

    def _on_credential_deleted(self, tab_id: str, cred_id: str):
        self.controller.handle_delete_credential(tab_id, cred_id)
        self.vault_data = self.controller._last_decrypted_data
        self._switch_tab(tab_id)
        self.show_message("Credencial movida a Eliminados.", "success")

    def _on_purge_credential(self, cred: dict):
        del_tab = get_tab(self.vault_data, DELETED_TAB_ID)
        if del_tab:
            del_tab["credentials"] = [
                c for c in del_tab["credentials"] if c["id"] != cred["id"]
            ]
        self._persist_silent()
        self.vault_data = self.controller._last_decrypted_data
        self._switch_tab(DELETED_TAB_ID)
        self.show_message("Credencial eliminada permanentemente.", "success")

    # ══════════════════════════════════════════════════════════════════════
    # NEW TAB DIALOG
    # ══════════════════════════════════════════════════════════════════════

    def _show_new_tab_dialog(self):
        self._dismiss_add_panel()
        if self._new_tab_dialog:
            self._dismiss_new_tab_dialog()
            return

        self._new_tab_dialog = NewTabDialog(
            master=self,
            on_confirm=self._on_new_tab_confirmed,
            on_cancel=self._dismiss_new_tab_dialog
        )
        self._new_tab_dialog.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

    def _dismiss_new_tab_dialog(self):
        if self._new_tab_dialog:
            self._new_tab_dialog.place_forget()
            self._new_tab_dialog.destroy()
            self._new_tab_dialog = None

    def _on_new_tab_confirmed(self, name: str, icon: str, fields: list):
        new_tab = self.controller.handle_add_tab(name, icon, fields)
        self.vault_data = self.controller._last_decrypted_data
        self._dismiss_new_tab_dialog()
        self._rebuild_tab_bar()
        self._switch_tab(new_tab["id"])
        self.show_message(f"Pestaña '{name}' creada.", "success")

    # ══════════════════════════════════════════════════════════════════════
    # DELETE TAB
    # ══════════════════════════════════════════════════════════════════════

    def _on_delete_tab(self, tab_id: str):
        ok = self.controller.handle_delete_tab(tab_id)
        if ok:
            self.vault_data = self.controller._last_decrypted_data
            self._rebuild_tab_bar()
            first = next(
                (t for t in self.vault_data.get("tabs", []) if t["id"] != DELETED_TAB_ID),
                None
            )
            if first:
                self._switch_tab(first["id"])
            self.show_message("Pestaña eliminada. Credenciales movidas a Eliminados.", "success")

    # ══════════════════════════════════════════════════════════════════════
    # RENAME VAULT
    # ══════════════════════════════════════════════════════════════════════

    def _show_rename_form(self):
        current = self.controller.storage.get_name_without_extension()
        self._rename_entry.delete(0, 'end')
        self._rename_entry.insert(0, current)
        self._rename_msg.configure(text="")
        self._rename_frame.pack(fill="x", padx=16, pady=(0, 6))
        self._rename_entry.focus_set()

    def _hide_rename_form(self):
        self._rename_frame.pack_forget()

    def _submit_rename(self):
        new_name = self._rename_entry.get().strip()
        if not new_name:
            self._rename_msg.configure(text="El nombre no puede estar vacío.",
                                       text_color="#ff4d4d")
            return
        success = self.controller.handle_rename_vault(new_name)
        if success:
            self._title_label.configure(
                text=f"🗄  {self.controller.storage.get_name_without_extension()}"
            )
            self._hide_rename_form()
            self.show_message(f"Renombrado a '{new_name}.data'", "success")

    # ══════════════════════════════════════════════════════════════════════
    # READ-ONLY
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_readonly(self):
        is_ro = (self._readonly_switch.get() == 1)
        self.controller.read_only = is_ro
        self._apply_readonly(is_ro)
        self.show_message(
            "Modo Solo Lectura activado." if is_ro else "Modo de edición activado.",
            "info" if is_ro else "success"
        )
        tab = self._active_tab()
        if tab:
            self._render_tab(tab)
            self._refresh_footer(tab)

    def _apply_readonly(self, is_ro: bool):
        self._btn_add.configure(
            state="disabled" if is_ro else "normal",
            fg_color="#3a3a3a" if is_ro else _ACCENT
        )

    # ══════════════════════════════════════════════════════════════════════
    # STANDARD INTERFACE (called by orchestrator)
    # ══════════════════════════════════════════════════════════════════════

    def show_message(self, text: str, msg_type: str = "info"):
        color = "#ff4d4d" if msg_type == "error" else _ACCENT
        self._msg_label.configure(text=text, text_color=color)

    def toggle_loading(self, is_loading: bool):
        if self._btn_sync:
            self._btn_sync.configure(
                state="disabled" if is_loading else "normal",
                text="Sincronizando..." if is_loading else "🔄 Sync"
            )

    def update_sync_ui(self):
        self._status_indicator.configure(text="● Sincronizado", text_color=_ACCENT)
        if self._btn_sync:
            self._btn_sync.pack_forget()
            self._btn_sync = None

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _active_tab(self) -> dict | None:
        if not self._active_tab_id:
            return None
        return next(
            (t for t in self.vault_data.get("tabs", []) if t["id"] == self._active_tab_id),
            None
        )

    def _persist_silent(self):
        """Save vault without going through a full orchestrator flow."""
        self.controller._persist(self.vault_data)