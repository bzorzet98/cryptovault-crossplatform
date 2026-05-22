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
from src.ui.theme import load_icon
import src.ui.theme as theme
import os
from PIL import Image


_ACCENT     = theme.c("accent")
_RED        = theme.c("danger")
_GREY       = "#888888"
_TAB_ON     = theme.c("accent")
_TAB_OFF    = "#2a2a2a"

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
        
        # ICONS
        self._icon_sync = load_icon("sync_white.png", size=(16,16))
        self._icon_no_sync = load_icon("no_sync.png", size=(16,16))
        self._icon_database = load_icon("database.png", size=(24,24))
        self._icon_arrow_back = load_icon("arrow_back.png", size=(18,18))
        self._icon_close = load_icon("close.png", size=(18,18))
        self._icon_cancel = load_icon("cancel.png", size=(18,18))
        self._icon_add = load_icon("add.png", size=(18,18))
        self._icon_download = load_icon("download.png", size=(18,18))
        self._icon_search = load_icon("search.png", size=(16,16))
        self._icon_delete_trashbucket = load_icon("delete_trashbucket.png", size=(16,16))
        self._icon_restore_from_trash = load_icon("restore_from_trash.png", size=(16,16))

        # Purge old deleted credentials silently on open
        if purge_old_deleted(self.vault_data):
            self._persist_silent()

        self._build_header()
        self._build_main_layout()

        # Select first non-deleted tab
        first = next(
            (t for t in self.vault_data.get("tabs", []) if t["id"] != DELETED_TAB_ID),
            None
        )
        if first:
            self._switch_tab(first["id"])
        
        self._current_tab_id = None
        
    # ══════════════════════════════════════════════════════════════════════
    # BUILD
    # ══════════════════════════════════════════════════════════════════════
    def _build_main_layout(self):
        self._main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self._main.pack(
            fill="both",
            expand=True
        )

        # ── Sidebar ─────────────────────────────
        self._sidebar = ctk.CTkFrame(
            self._main,
            width=220,
            fg_color=theme.c("sidebar"),
            corner_radius=0
        )
        self._sidebar.pack(
            side="left",
            fill="y"
        )
        self._sidebar.pack_propagate(False)

        # ── Content ─────────────────────────────
        self._content = ctk.CTkFrame(
            self._main,
            fg_color="transparent"
        )
        self._content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(1, 0)
        )

        self._build_sidebar()
        self._build_body_inside_content()
        
    def _build_header(self):
        header = ctk.CTkFrame(
                self,
                fg_color="#181818",
                height=56,
                corner_radius=0
            )

        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        inner.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=8
        )
        # ── Left spacer ───────────────────────────
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        # ── Center title ─────────────────────────
        center = ctk.CTkFrame(inner, fg_color="transparent")
        center.pack(side="left", expand=True)

        vault_name = self.controller.storage.get_name_without_extension()

        self._title_label = ctk.CTkLabel(
            center,
            text=vault_name,
            image=self._icon_database,
            compound="left",
            font=theme.font(22, "bold"),
            cursor="hand2"
        )

        self._title_label.pack(expand=True)

        self._title_label.bind(
            "<Button-1>",
            lambda e: self._show_rename_form()
        )

        # ── Right actions ────────────────────────
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")

        is_sync = getattr(self.controller, 'drive_source', False)

        status_color = _ACCENT if is_sync else _GREY
        status_text = " Sincronizado" if is_sync else " Local"

        icon_sync = (
            self._icon_sync
            if is_sync else
            self._icon_no_sync
        )

        self._status_indicator = ctk.CTkLabel(
            right,
            text=status_text,
            image=icon_sync,
            compound="left",
            text_color=status_color,
            font=theme.font(12)
        )

        self._status_indicator.pack(side="left", padx=(0, 10))

        self._msg_label = ctk.CTkLabel(
            right,
            text="",
            font=theme.font(12),
            text_color=_ACCENT
        )

        self._msg_label.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            right,
            text="",
            width=32,
            height=30,
            image=self._icon_arrow_back,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color=theme.c("hover"),
            command=lambda:
                self.controller.handle_exit(
                    then_quit=False
                )
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            right,
            text="",
            width=32,
            height=30,
            image=self._icon_close,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color=theme.c("hover"),
            command=lambda:
                self.controller.handle_exit(
                    then_quit=True
                )
        ).pack(side="left")

        self._msg_label = ctk.CTkLabel(
            inner,
            text="",
            font=theme.font(12),
            text_color=_ACCENT
        )

        self._msg_label.pack(side="right", padx=(0, 12))

        # ── Rename form (hidden) ──────────────────────────────────────────
        self._rename_frame = ctk.CTkFrame(self, fg_color="#222222", corner_radius=8)
        ri = ctk.CTkFrame(self._rename_frame, fg_color="transparent")
        ri.pack(padx=14, pady=10, fill="x")
        ctk.CTkLabel(ri, text="Nuevo nombre:", font=theme.font(12),
                     text_color=theme.c("text_secondary")).pack(anchor="w")
        row = ctk.CTkFrame(ri, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        self._rename_entry = ctk.CTkEntry(row, placeholder_text="nombre_boveda", width=200)
        self._rename_entry.pack(side="left", padx=(0, 6))
        self._rename_entry.bind("<Return>", lambda e: self._submit_rename())
        ctk.CTkLabel(row, text=".data", font=theme.font(12),
                     text_color="#666666").pack(side="left")
        btn_row = ctk.CTkFrame(ri, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(8, 0))
        ctk.CTkButton(btn_row, text="Renombrar", width=110,
                      command=self._submit_rename).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancelar", width=80,
                      fg_color="transparent", border_width=1,
                      border_color="#555555", text_color=theme.c("text_secondary"), hover_color=theme.c("hover"),
                      command=self._hide_rename_form).pack(side="left")
        self._rename_msg = ctk.CTkLabel(ri, text="", font=theme.font(11))
        self._rename_msg.pack(anchor="w", pady=(4, 0))

    def _build_body_inside_content(self):
        # ── Search bar ─────────────────────────────────────────────
        search_row = ctk.CTkFrame(self._content, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(4, 0))

        search_box = ctk.CTkFrame(
                    search_row,
                    fg_color=theme.c("card"),
                    border_width=1,
                    border_color="#3F3F3F",
                    corner_radius=6,
                    height=36
                )

        search_box.pack(fill="x")

        # icono
        search_icon = ctk.CTkLabel(
            search_box,
            text="",
            image=self._icon_search,
            width=20
        )
        search_icon.pack(side="left", padx=(8, 4))

        # variable
        self._search_var = ctk.StringVar()
        self._search_var.trace_add(
            "write",
            lambda *_: self._on_search_change()
        )

        # entry
        self.search_entry = ctk.CTkEntry(
            search_box,
            textvariable=self._search_var,
            placeholder_text="Buscar credencial...",
            border_width=1,
            corner_radius=8,
            fg_color="transparent",
            text_color="#EAEAEA",
            placeholder_text_color="#7A7A7A",
            height=32
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )
        ####### Toool bar
        toolbar = ctk.CTkFrame(
                                self._content,
                                fg_color="transparent"
                            )

        toolbar.pack(
            fill="x",
            padx=16,
            pady=(8, 0)
        )
        self._btn_add = ctk.CTkButton(
            toolbar,
            text="Nueva credencial",
            image=self._icon_add,
            compound="left",
            height=34,
            fg_color=_ACCENT,
            hover_color=theme.c("accent_hover"),
            command=self._show_add_panel
        )

        self._btn_add.pack(side="left")

        # ── Scroll body ────────────────────────────────────────────
        self._body = ctk.CTkScrollableFrame(
            self._content,
            fg_color="transparent"
        )

        self._body.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(10, 6)
        )
    
    def _on_search_change(self):
        """Re-render active tab filtered by search query."""
        tab = self._active_tab()
        if tab:
            self._render_tab(tab)
            
    def _build_sidebar(self):
        
        ctk.CTkLabel(
                    self._sidebar,
                    text="SECCIONES",
                    text_color="#777777",
                    font=theme.font(11, "bold")
                ).pack(anchor="w", padx=12, pady=(10, 4))

        # ── Tabs ─────────────────────────────
        self._tabs_frame = ctk.CTkScrollableFrame(
            self._sidebar,
            fg_color="transparent"
        )

        self._tabs_frame.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=(8, 4)
        )

        # tabs
        self._rebuild_sidebar_tabs()

        ctk.CTkFrame(
                self._sidebar,
                height=1,
                fg_color="#2a2a2a"
            ).pack(fill="x", padx=8, pady=8)
        

        # ── Bottom actions ───────────────────
        bottom = ctk.CTkFrame(
            self._sidebar,
            fg_color="transparent"
        )
        bottom.pack(
            fill="x",
            padx=8,
            pady=8
        )
        
        ctk.CTkLabel(
            bottom,
            text="ACCIONES",
            text_color="#777777",
            font=theme.font(11, "bold")
        ).pack(anchor="w", pady=(0, 6))
        

        ctk.CTkButton(
            bottom,
            text="Exportar",
            image=self._icon_download,
            compound="left",
            height=32,
            fg_color="transparent",
            hover_color="#2a2a2a",
            anchor="w",
            command=self.controller.handle_export_vault
        ).pack(fill="x", pady=(0, 6))

        if not getattr(self.controller, 'drive_source', False):

            self._btn_sync = ctk.CTkButton(
                bottom,
                text="Sync Drive",
                image=self._icon_sync,
                compound="left",
                height=32,
                fg_color="transparent",
                hover_color="#2a2a2a",
                anchor="w",
                command=lambda:
                    self.controller.handle_sync_drive(
                        then_quit=False
                    )
            )

            self._btn_sync.pack(fill="x", pady=(0, 6))

        self._readonly_switch = ctk.CTkSwitch(
            bottom,
            text="Solo lectura",
            command=self._toggle_readonly
        )

        self._readonly_switch.pack(
            anchor="w",
            pady=(8, 0)
        )
        
        ctk.CTkButton(
                        bottom,
                        text="Nueva categoría",
                        image=self._icon_add,
                        compound="left",
                        height=32,
                        fg_color="transparent",
                        hover_color="#2a2a2a",
                        anchor="w",
                        command=self._show_new_tab_dialog
                    ).pack(fill="x", pady=(0, 4))

        
    def _rebuild_sidebar_tabs(self):
        for w in self._tabs_frame.winfo_children():
            w.destroy()

        self._tab_buttons = {}

        normal_tabs = []
        deleted_tab = None

        for tab in self.vault_data.get("tabs", []):

            if tab["id"] == DELETED_TAB_ID:
                deleted_tab = tab
            else:
                normal_tabs.append(tab)

        # normales
        for tab in normal_tabs:
            self._add_sidebar_tab(tab)

        # separador visual
        if deleted_tab:

            ctk.CTkFrame(
                self._tabs_frame,
                height=1,
                fg_color="#2a2a2a"
            ).pack(fill="x", padx=4, pady=8)

            self._add_sidebar_tab(deleted_tab)

    def _add_sidebar_tab(self, tab):
        
        btn = ctk.CTkButton(
            self._tabs_frame,
            text=tab['name'],
            height=36,
            anchor="w",
            fg_color="transparent",
            hover_color="#2a2a2a",
            command=lambda tid=tab["id"]: self._switch_tab(tid)
        )
        btn.pack(
            fill="x",
            pady=2
        )

        self._tab_buttons[tab["id"]] = btn

    # ══════════════════════════════════════════════════════════════════════
    # TAB SWITCHING & RENDERING
    # ══════════════════════════════════════════════════════════════════════

    def _switch_tab(self, tab_id: str):
        self._dismiss_add_panel()
        self._dismiss_new_tab_dialog()

        self._active_tab_id = tab_id

        self._update_tab_styles()
        
        tab = next(
            (t for t in self.vault_data.get("tabs", []) if t["id"] == tab_id), None
        )
        if tab:
            self._render_tab(tab)

    def _update_tab_styles(self):

        for tid, btn in self._tab_buttons.items():

            active = tid == self._active_tab_id

            btn.configure(
                fg_color=_TAB_ON if active else "transparent",
                hover_color=theme.c("accent_hover") if active else "#2a2a2a",
                text_color="#ffffff" if active else "#cccccc"
            )
            
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
                text_color=_GREY, font=theme.font(13)
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
        card = ctk.CTkFrame(self._body, fg_color=theme.c("card"), corner_radius=10)
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            inner, text=cred["name"],
            font=theme.font(14, "bold"), anchor="w"
        ).pack(side="left")

        deleted_at = cred.get("deleted_at", "")
        if deleted_at:
            ctk.CTkLabel(
                inner, text=f"  eliminado: {deleted_at[:10]}",
                font=theme.font(11), text_color=_GREY
            ).pack(side="left")

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(side="right")

        # Restaurar
        ctk.CTkButton(
            btn_frame, text="Restaurar", width=90, height=28,
            image=self._icon_restore_from_trash,
            compound="left",
            fg_color="#2a4a3a", hover_color=theme.c("accent_hover"),
            font=theme.font(12),
            command=lambda c=cred: self._show_restore_picker(c)
        ).pack(side="left", padx=(0, 6))

        # Borrar 
        ctk.CTkButton(
            btn_frame, text="Borrar", width=80, height=28,
            image=self._icon_delete_trashbucket,
            compound="left",
            fg_color=_RED, hover_color="#7a2020",
            font=theme.font(12),
            command=lambda c=cred: self._on_purge_credential(c)
        ).pack(side="left")

    def _show_restore_picker(self, cred: dict):
        picker = ctk.CTkToplevel(self)

        picker.title("Restaurar credencial")
        picker.configure(fg_color="#1b1b1b")

        # tamaño más cómodo
        width = 360
        height = 480

        # centrar
        screen_w = picker.winfo_screenwidth()
        screen_h = picker.winfo_screenheight()

        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))

        picker.geometry(f"{width}x{height}+{x}+{y}")

        picker.resizable(False, False)

        # modal
        picker.transient(self)
        picker.grab_set()

        # ── Header ─────────────────────────────────────
        ctk.CTkLabel(
            picker,
            text="Restaurar credencial",
            font=theme.font(18, "bold")
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            picker,
            text="Seleccioná la categoría destino",
            text_color="#888888",
            font=theme.font(12)
        ).pack(pady=(0, 14))

        # ── Scroll area ───────────────────────────────
        frame = ctk.CTkScrollableFrame(
            picker,
            fg_color="transparent"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 10)
        )

        # tabs
        for tab in self.vault_data.get("tabs", []):

            if tab["id"] == DELETED_TAB_ID:
                continue

            ctk.CTkButton(
                frame,
                text=tab["name"],
                height=40,
                anchor="w",
                fg_color="#2a2a2a",
                hover_color=theme.c("hover"),
                font=theme.font(13),
                command=lambda tid=tab["id"]:
                    self._do_restore(cred, tid, picker)
            ).pack(
                fill="x",
                pady=4
            )

        # ── Footer ────────────────────────────────────
        footer = ctk.CTkFrame(
            picker,
            fg_color="transparent"
        )

        footer.pack(
            fill="x",
            padx=14,
            pady=(0, 14)
        )

        ctk.CTkButton(
            footer,
            text="Cancelar",
            image=self._icon_cancel,
            compound="left",
            height=36,
            fg_color="#444444",
            hover_color=theme.c("hover"),
            command=picker.destroy
        ).pack(fill="x")

    def _do_restore(self, cred: dict, target_tab_id: str, picker):

        picker.destroy()

        self.controller.handle_restore_credential(
            cred["id"],
            target_tab_id
        )

        self.vault_data = self.controller._last_decrypted_data

        # refrescar sidebar/tabs
        self._rebuild_sidebar_tabs()

        # ir a la pestaña restaurada
        self._switch_tab(target_tab_id)

        self.show_message("Credencial restaurada")


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

    def _on_new_tab_confirmed(self, name: str,  fields: list):
        new_tab = self.controller.handle_add_tab(name, fields)
        self.vault_data = self.controller._last_decrypted_data
        self._dismiss_new_tab_dialog()
        self._rebuild_sidebar_tabs()
        self._switch_tab(new_tab["id"])
        self.show_message(f"Pestaña '{name}' creada.", "success")

    # ══════════════════════════════════════════════════════════════════════
    # DELETE TAB
    # ══════════════════════════════════════════════════════════════════════

    def _on_delete_tab(self, tab_id: str):
        ok = self.controller.handle_delete_tab(tab_id)
        if ok:
            self.vault_data = self.controller._last_decrypted_data
            self._rebuild_sidebar_tabs()
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
                text=f"  {self.controller.storage.get_name_without_extension()}",
                image=self._icon_database, compound="left"
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
                text="Sincronizando..." if is_loading else " Sync"
            )

    def update_sync_ui(self):
        self._status_indicator.configure(text=" Sincronizado", text_color=_ACCENT,
                                         image=self._icon_sync, compound="left")
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