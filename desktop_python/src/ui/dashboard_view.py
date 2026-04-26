import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    """
    Main vault view.

    Layout:
        ┌─────────────────────────────────────────────────┐
        │ 🗄 vault_name          ● Sync/Local  ← Menú  🔒│  header
        ├─────────────────────────────────────────────────┤
        │ [+ Agregar]  [📤 Exportar]     [🔄 Sync Drive] │  action bar
        ├─────────────────────────────────────────────────┤
        │ (status message)                                │
        ├─────────────────────────────────────────────────┤
        │ scrollable credential list                      │
        └─────────────────────────────────────────────────┘

    Rules:
        - "🔄 Sync Drive" appears only when drive_source=False (local vault).
        - Once synced (drive_source=True), the button disappears and status shows "● Sincronizado".
        - "📤 Exportar" is always visible.
        - Solo Lectura switch disables adding credentials.
    """

    def __init__(self, master, controller, data: dict):
        super().__init__(master)
        self.controller = controller
        self.vault_data  = data

        is_sync = getattr(controller, 'drive_source', False)

        # ══════════════════════════════════════════════════════════════════
        # HEADER
        # ══════════════════════════════════════════════════════════════════
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 6))

        # Left: vault name (clickable to rename)
        vault_name = controller.storage.get_name_without_extension()
        self.title_label = ctk.CTkLabel(
            header,
            text=f"🗄  {vault_name}",
            font=("Roboto", 19, "bold"),
            cursor="hand2"
        )
        self.title_label.pack(side="left")
        self.title_label.bind("<Button-1>", lambda e: self._show_rename_form())

        # Right: status pill + Menú + Cerrar
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        status_color = "#2c8558" if is_sync else "#888888"
        status_text  = "● Sincronizado" if is_sync else "● Local"
        self.status_indicator = ctk.CTkLabel(
            right, text=status_text,
            text_color=status_color, font=("Roboto", 12)
        )
        self.status_indicator.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            right, text="← Menú",
            width=72, height=30,
            fg_color="transparent", border_width=1,
            border_color="#555555", text_color="#aaaaaa",
            hover_color="#333333",
            command=lambda: controller.handle_exit(then_quit=False)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            right, text="🔒 Cerrar",
            width=80, height=30,
            fg_color="#444444",
            command=lambda: controller.handle_exit(then_quit=True)
        ).pack(side="left")

        # ══════════════════════════════════════════════════════════════════
        # RENAME FORM  (hidden by default)
        # ══════════════════════════════════════════════════════════════════
        self.rename_frame = ctk.CTkFrame(self, fg_color="#222222", corner_radius=8)

        ri = ctk.CTkFrame(self.rename_frame, fg_color="transparent")
        ri.pack(padx=14, pady=10, fill="x")

        ctk.CTkLabel(
            ri, text="Nuevo nombre del archivo:",
            font=("Roboto", 12), text_color="#aaaaaa"
        ).pack(anchor="w")

        row = ctk.CTkFrame(ri, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))

        self.rename_entry = ctk.CTkEntry(row, placeholder_text="ej: trabajo_vault", width=200)
        self.rename_entry.pack(side="left", padx=(0, 6))
        self.rename_entry.bind("<Return>", lambda e: self._submit_rename())

        ctk.CTkLabel(row, text=".data", font=("Roboto", 12), text_color="#666666").pack(side="left")

        btn_row = ctk.CTkFrame(ri, fg_color="transparent")
        btn_row.pack(anchor="w", pady=(8, 0))

        ctk.CTkButton(btn_row, text="Renombrar", width=110, command=self._submit_rename).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancelar", width=80, fg_color="#444444", hover_color="#333333",
                      command=self._hide_rename_form).pack(side="left")

        self.rename_msg = ctk.CTkLabel(ri, text="", font=("Roboto", 11))
        self.rename_msg.pack(anchor="w", pady=(4, 0))

        # ══════════════════════════════════════════════════════════════════
        # ACTION BAR
        # ══════════════════════════════════════════════════════════════════
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=16, pady=(4, 0))

        # Left group: Add + Export
        left_group = ctk.CTkFrame(action_bar, fg_color="transparent")
        left_group.pack(side="left")

        self.btn_add = ctk.CTkButton(
            left_group, text="+ Agregar",
            width=110, height=34,
            command=self.toggle_add_form
        )
        self.btn_add.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            left_group, text="📤 Exportar",
            width=100, height=34,
            fg_color="#3a3a3a", hover_color="#4a4a4a",
            command=controller.handle_export_vault
        ).pack(side="left")

        # Right group: Sync Drive — only when local
        if not is_sync:
            self.btn_sync = ctk.CTkButton(
                action_bar, text="🔄 Sync Drive",
                width=120, height=34,
                fg_color="#2c8558", hover_color="#1e5c3d",
                command=lambda: controller.handle_sync_drive(then_quit=False)
            )
            self.btn_sync.pack(side="right")
        else:
            self.btn_sync = None  # Nothing on the right when already in Drive

        # Solo Lectura switch (far right after sync)
        self.readonly_switch = ctk.CTkSwitch(
            action_bar, text="Solo Lectura",
            command=self._toggle_readonly,
            width=100
        )
        self.readonly_switch.pack(side="right", padx=(0, 12))
        if getattr(controller, 'read_only', False):
            self.readonly_switch.select()

        # ══════════════════════════════════════════════════════════════════
        # STATUS MESSAGE
        # ══════════════════════════════════════════════════════════════════
        self.message_label = ctk.CTkLabel(self, text="", font=("Roboto", 12))
        self.message_label.pack(pady=(6, 0))

        # ══════════════════════════════════════════════════════════════════
        # ADD CREDENTIAL FORM  (hidden by default)
        # ══════════════════════════════════════════════════════════════════
        self.form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)

        ctk.CTkLabel(self.form_frame, text="Nueva Credencial",
                     font=("Roboto", 15, "bold")).pack(pady=(12, 4))

        self.entry_name = ctk.CTkEntry(
            self.form_frame, placeholder_text="Servicio (ej: Netflix)", width=260
        )
        self.entry_name.pack(pady=4)

        self.entry_user = ctk.CTkEntry(
            self.form_frame, placeholder_text="Usuario / Email", width=260
        )
        self.entry_user.pack(pady=4)

        self.entry_pass = ctk.CTkEntry(
            self.form_frame, placeholder_text="Contraseña", show="*", width=260
        )
        self.entry_pass.pack(pady=4)

        form_btns = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form_btns.pack(pady=10)
        ctk.CTkButton(form_btns, text="Guardar", width=100,
                      command=self.submit_form).pack(side="left", padx=5)
        ctk.CTkButton(form_btns, text="Cancelar", width=100,
                      fg_color="#555555", command=self.toggle_add_form).pack(side="right", padx=5)

        # ══════════════════════════════════════════════════════════════════
        # PASSWORD LIST
        # ══════════════════════════════════════════════════════════════════
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Contraseñas Guardadas")
        self.scroll_frame.pack(fill="both", expand=True, padx=16, pady=12)

        self.render(data)

        # Apply read_only state to btn_add if active
        if getattr(controller, 'read_only', False):
            self._apply_readonly(True)

    # ══════════════════════════════════════════════════════════════════════
    # RENAME
    # ══════════════════════════════════════════════════════════════════════

    def _show_rename_form(self):
        current = self.controller.storage.get_name_without_extension()
        self.rename_entry.delete(0, 'end')
        self.rename_entry.insert(0, current)
        self.rename_msg.configure(text="")
        self.rename_frame.pack(fill="x", padx=16, pady=(0, 6))
        self.rename_entry.focus_set()

    def _hide_rename_form(self):
        self.rename_frame.pack_forget()

    def _submit_rename(self):
        new_name = self.rename_entry.get().strip()
        if not new_name:
            self.rename_msg.configure(text="El nombre no puede estar vacío.", text_color="#ff4d4d")
            return
        success = self.controller.handle_rename_vault(new_name)
        if success:
            self.title_label.configure(
                text=f"🗄  {self.controller.storage.get_name_without_extension()}"
            )
            self._hide_rename_form()
            self.show_message(f"Renombrado a '{new_name}.data'", "success")

    # ══════════════════════════════════════════════════════════════════════
    # ADD CREDENTIAL FORM
    # ══════════════════════════════════════════════════════════════════════

    def toggle_add_form(self):
        if getattr(self.controller, 'read_only', False):
            return
        if self.form_frame.winfo_ismapped():
            self.form_frame.pack_forget()
            self.entry_name.delete(0, 'end')
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            self.btn_add.configure(state="normal")
        else:
            self.form_frame.pack(after=self.message_label, fill="x", padx=16, pady=4)
            self.btn_add.configure(state="disabled")

    def submit_form(self):
        n, u, p = self.entry_name.get(), self.entry_user.get(), self.entry_pass.get()
        if n and u and p:
            self.controller.handle_save_credential(n, u, p)
            self.toggle_add_form()
        else:
            self.show_message("Por favor, completa todos los campos.", "error")

    # ══════════════════════════════════════════════════════════════════════
    # READ-ONLY TOGGLE
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_readonly(self):
        is_ro = (self.readonly_switch.get() == 1)
        self.controller.read_only = is_ro
        self._apply_readonly(is_ro)
        msg = "Modo Solo Lectura activado." if is_ro else "Modo de edición activado."
        self.show_message(msg, "info" if is_ro else "success")

    def _apply_readonly(self, is_ro: bool):
        if is_ro:
            self.btn_add.configure(state="disabled", fg_color="#3a3a3a")
        else:
            self.btn_add.configure(state="normal", fg_color=("#2c8558", "#2c8558"))

    # ══════════════════════════════════════════════════════════════════════
    # RENDER / LIST
    # ══════════════════════════════════════════════════════════════════════

    def render(self, data: dict):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        items = data.get("items", [])
        if not items:
            ctk.CTkLabel(
                self.scroll_frame,
                text="Tu bóveda está vacía. Agrega tu primera credencial.",
                text_color="gray"
            ).pack(pady=24)
            return

        for item in items:
            self._build_row(item["name"], item["username"], item["password"])

    def _build_row(self, title: str, user: str, password: str):
        row = ctk.CTkFrame(self.scroll_frame, corner_radius=6)
        row.pack(fill="x", pady=4)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=12, pady=8)

        ctk.CTkLabel(info, text=title, font=("Roboto", 14, "bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=user, font=("Roboto", 12), text_color="#888888",
                     anchor="w").pack(anchor="w")

        ctk.CTkButton(
            row, text="Copiar", width=72, height=30,
            fg_color="#333333", hover_color="#444444",
            command=lambda p=password: self.copy_to_clipboard(p)
        ).pack(side="right", padx=10, pady=8)

    def copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_message("¡Contraseña copiada al portapapeles!", "success")

    # ══════════════════════════════════════════════════════════════════════
    # STANDARD INTERFACE METHODS
    # ══════════════════════════════════════════════════════════════════════

    def show_message(self, text: str, msg_type: str = "info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)

    def toggle_loading(self, is_loading: bool):
        if self.btn_sync:
            if is_loading:
                self.btn_sync.configure(state="disabled", text="Sincronizando...")
            else:
                self.btn_sync.configure(state="normal", text="🔄 Sync Drive")

    def update_sync_ui(self):
        """Called after a successful sync to update status pill and hide Sync button."""
        self.status_indicator.configure(text="● Sincronizado", text_color="#2c8558")
        if self.btn_sync:
            self.btn_sync.pack_forget()
            self.btn_sync = None