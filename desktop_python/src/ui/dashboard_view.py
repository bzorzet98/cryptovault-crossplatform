import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller, data):
        super().__init__(master)
        self.controller = controller
        self.vault_data = data

        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="Mi Bóveda", font=("Roboto", 22, "bold")).pack(side="left")
        
        status_color = "#2c8558" if getattr(controller, 'mode', 'NORMAL') == "SYNC" else "#888888"
        status_text = "● Sincronizado" if status_color == "#2c8558" else "● Local"
        
        self.status_indicator = ctk.CTkLabel(header, text=status_text, text_color=status_color, font=("Roboto", 12))
        self.status_indicator.pack(side="right", padx=15)
        
        ctk.CTkButton(header, text="Salir", width=60, fg_color="#444444", 
                      command=self.controller.handle_logout).pack(side="right")

        # --- ACCIONES ---
        self.actions = ctk.CTkFrame(self)
        self.actions.pack(fill="x", padx=20, pady=10)
        
        self.btn_add = ctk.CTkButton(self.actions, text="+ Agregar Credencial", 
                                     command=self.toggle_add_form)
        self.btn_add.pack(side="left", padx=10, pady=10)
        
        # Botón de Sincronización
        self.btn_sync = ctk.CTkButton(self.actions, text="🔄 Sync Drive", 
                                      fg_color="#2c8558", hover_color="#1e5c3d",
                                      command=self.controller.handle_sync_drive)
        self.btn_sync.pack(side="right", padx=10, pady=10)

        # BOTÓN DE DESVINCULAR (Solo aparece si el modo es SYNC)
        if getattr(self.controller, 'mode', 'NORMAL') == "SYNC":
            self.btn_unlink = ctk.CTkButton(
                            self.top_frame, text="🔓 Desvincular Drive", 
                            command=self.controller.handle_unlink_drive,
                            fg_color="#a13d3d", hover_color="#7a2e2e"
                        )
            self.btn_unlink.pack(side="right", padx=10)
        else:
            self.btn_sync = ctk.CTkButton(
                self.top_frame, text="🔄 Sync Drive", 
                command=self.controller.handle_sync_drive,
                fg_color="#2c8558", hover_color="#1e5c3d"
            )
            self.btn_sync.pack(side="right", padx=10)
        # Modo Lectura
        if getattr(self.controller, 'mode', 'NORMAL') == "READ_ONLY":
            self.btn_add.configure(state="disabled", text="🔒 Modo Lectura")
            self.btn_sync.pack_forget()

        # ---> ¡AGREGA ESTAS DOS LÍNEAS AQUÍ! <---
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=5)

        # Luego sigue tu código normal del panel de formulario...
        self.form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        # --- PANEL DE FORMULARIO OCULTO (NUEVO) ---
        self.form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        # No le hacemos pack() aquí para que empiece oculto

        ctk.CTkLabel(self.form_frame, text="Nueva Credencial", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.entry_name = ctk.CTkEntry(self.form_frame, placeholder_text="Servicio (ej: Netflix)", width=250)
        self.entry_name.pack(pady=5)
        
        self.entry_user = ctk.CTkEntry(self.form_frame, placeholder_text="Usuario / Email", width=250)
        self.entry_user.pack(pady=5)
        
        self.entry_pass = ctk.CTkEntry(self.form_frame, placeholder_text="Contraseña", show="*", width=250)
        self.entry_pass.pack(pady=5)

        form_buttons = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        form_buttons.pack(pady=10)
        
        ctk.CTkButton(form_buttons, text="Guardar", width=100, command=self.submit_form).pack(side="left", padx=5)
        ctk.CTkButton(form_buttons, text="Cancelar", width=100, fg_color="#555555", command=self.toggle_add_form).pack(side="right", padx=5)

        # --- LISTA DE CONTRASEÑAS ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Contraseñas Guardadas")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.render(data)

    # --- MÉTODOS DE LA INTERFAZ ---

    def toggle_add_form(self):
        """Muestra u oculta el panel para agregar credenciales."""
        if self.form_frame.winfo_ismapped():
            # Si está visible, lo ocultamos y limpiamos las cajas
            self.form_frame.pack_forget()
            self.entry_name.delete(0, 'end')
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            self.btn_add.configure(state="normal")
        else:
            # Si está oculto, lo mostramos justo arriba de la lista
            self.form_frame.pack(after=self.message_label, fill="x", padx=20, pady=5)
            self.btn_add.configure(state="disabled")

    def submit_form(self):
        """Valida y envía la nueva credencial al Orchestrator."""
        n = self.entry_name.get()
        u = self.entry_user.get()
        p = self.entry_pass.get()
        
        if n and u and p:
            self.controller.handle_save_credential(n, u, p)
            self.toggle_add_form() # Ocultar formulario al terminar
        else:
            self.show_message("Por favor, llena todos los campos", "error")

    # --- MÉTODOS ESTÁNDAR (Igual que antes) ---

    def render(self, data):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        items = data.get("items", [])
        if not items:
            ctk.CTkLabel(self.scroll_frame, text="Tu bóveda está vacía.", text_color="gray").pack(pady=20)
            return

        for item_data in items:
            self._create_list_item(item_data["name"], item_data["username"], item_data["password"])

    def _create_list_item(self, title, user, password):
        item = ctk.CTkFrame(self.scroll_frame)
        item.pack(fill="x", pady=5)
        
        info_text = f"{title}  |  {user}"
        ctk.CTkLabel(item, text=info_text, font=("Roboto", 14)).pack(side="left", padx=10)
        
        btn_copy = ctk.CTkButton(item, text="Copiar Pass", width=80,
                                 command=lambda p=password: self.copy_to_clipboard(p))
        btn_copy.pack(side="right", padx=10, pady=5)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_message("¡Contraseña copiada!", "success")

    def toggle_loading(self, is_loading):
        if is_loading:
            self.btn_sync.configure(state="disabled", text="Sincronizando...")
        else:
            self.btn_sync.configure(state="normal", text="🔄 Sync Drive")

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)