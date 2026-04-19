import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller, data):
        super().__init__(master)
        self.controller = controller

        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="Mi Bóveda", font=("Roboto", 22, "bold")).pack(side="left")
        
        # El botón salir ahora llama directamente al Orchestrator
        ctk.CTkButton(header, text="Salir", width=60, fg_color="#444444", 
                      command=self.controller.handle_logout).pack(side="right")

        # --- ACCIONES ---
        self.actions = ctk.CTkFrame(self)
        self.actions.pack(fill="x", padx=20, pady=10)
        
        self.btn_add = ctk.CTkButton(self.actions, text="+ Agregar Credencial", 
                                     command=self.open_add_popup)
        self.btn_add.pack(side="left", padx=10, pady=10)
        
        self.btn_sync = ctk.CTkButton(self.actions, text="🔄 Sync Drive", 
                                      fg_color="#2c8558", hover_color="#1e5c3d",
                                      command=self.controller.handle_sync_drive)
        self.btn_sync.pack(side="right", padx=10, pady=10)

        # Lógica de "Solo Lectura"
        # Si el modo es READ_ONLY, desactivamos crear y ocultamos sincronizar
        if getattr(self.controller, 'mode', 'NORMAL') == "READ_ONLY":
            self.btn_add.configure(state="disabled", text="🔒 Modo Lectura")
            self.btn_sync.pack_forget()

        # Label para mensajes de éxito/error
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack()

        # --- LISTA DE CONTRASEÑAS ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Contraseñas Guardadas")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Renderizamos los datos que llegaron del Orchestrator
        self.render(data)

    # --- MÉTODOS ESTÁNDAR ---

    def render(self, data):
        """Limpia la lista actual y dibuja las credenciales del diccionario."""
        # 1. Limpiar los items viejos
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # 2. Dibujar los items nuevos
        items = data.get("items", [])
        if not items:
            ctk.CTkLabel(self.scroll_frame, text="Tu bóveda está vacía.", text_color="gray").pack(pady=20)
            return

        for item_data in items:
            self._create_list_item(item_data["name"], item_data["username"], item_data["password"])

    def _create_list_item(self, title, user, password):
        """Crea la fila visual para una sola contraseña."""
        item = ctk.CTkFrame(self.scroll_frame)
        item.pack(fill="x", pady=5)
        
        info_text = f"{title}  |  {user}"
        ctk.CTkLabel(item, text=info_text, font=("Roboto", 14)).pack(side="left", padx=10)
        
        # Botón para copiar la contraseña al portapapeles
        btn_copy = ctk.CTkButton(item, text="Copiar Pass", width=80,
                                 command=lambda p=password: self.copy_to_clipboard(p))
        btn_copy.pack(side="right", padx=10, pady=5)

    def copy_to_clipboard(self, text):
        """Copia el texto al portapapeles del sistema operativo."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.show_message("¡Contraseña copiada!", "success")

    def toggle_loading(self, is_loading):
        """Desactiva el botón de sync mientras sube a Drive."""
        if is_loading:
            self.btn_sync.configure(state="disabled", text="Sincronizando...")
        else:
            self.btn_sync.configure(state="normal", text="🔄 Sync Drive")

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else "#2c8558"
        self.message_label.configure(text=text, text_color=color)

    # --- POP-UP (NUEVA CREDENCIAL) ---

    def open_add_popup(self):
        """Abre una ventana emergente para añadir un nuevo dato."""
        popup = ctk.CTkToplevel(self)
        popup.title("Nueva Credencial")
        popup.geometry("300x350")
        popup.attributes("-topmost", True) # Mantener al frente
        popup.grab_set() # Bloquear la ventana principal mientras este popup esté abierto

        ctk.CTkLabel(popup, text="Agregar a Bóveda", font=("Roboto", 18, "bold")).pack(pady=15)

        entry_name = ctk.CTkEntry(popup, placeholder_text="Servicio (ej: Netflix)")
        entry_name.pack(pady=10, padx=20, fill="x")

        entry_user = ctk.CTkEntry(popup, placeholder_text="Usuario / Email")
        entry_user.pack(pady=10, padx=20, fill="x")

        entry_pass = ctk.CTkEntry(popup, placeholder_text="Contraseña", show="*")
        entry_pass.pack(pady=10, padx=20, fill="x")

        def submit_form():
            n = entry_name.get()
            u = entry_user.get()
            p = entry_pass.get()
            
            if n and u and p:
                # Enviar al cerebro (Orchestrator) para cifrar y guardar
                self.controller.handle_save_credential(n, u, p)
                popup.destroy() # Cerrar popup al terminar
            else:
                ctk.CTkLabel(popup, text="Llena todos los campos", text_color="red").pack()

        ctk.CTkButton(popup, text="Guardar", command=submit_form).pack(pady=20)