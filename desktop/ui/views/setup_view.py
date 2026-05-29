import customtkinter as ctk
from desktop.ui.themes.theme import load_icon
import desktop.ui.themes.theme as theme
from desktop.ui.widgets.password_generator import PasswordGeneratorWidget

class SetupView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller   = controller
        self._pw_visible  = False

        ctk.CTkLabel(
            self, text="Nueva Bóveda",
            font=theme.font(24, "bold")
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            self,
            text="Elige una Master Password para cifrar todos tus datos.\nNo podrás recuperarla si la olvidás.",
            font=theme.font(13), text_color="#888888", justify="center"
        ).pack(pady=(0, 24))

        # ── Back button ───────────────────────────────────

        back_bar = ctk.CTkFrame(self, fg_color="transparent")
        back_bar.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkButton(
            back_bar,
            text="Volver",
            image=self._icon_back,
            compound="left",
            width=90,
            height=28,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            text_color=theme.c("text_secondary"),
            hover_color=theme.c("hover"),
            command=self.controller.app.show_welcome_view
        ).pack(side="left")


        # ── Password field ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Master Password *",
                     font=theme.font(12), text_color=theme.c("text_secondary")).pack(anchor="center")

        pw_row = ctk.CTkFrame(self, fg_color="transparent")
        pw_row.pack(pady=(4, 10))

        self.password_entry = ctk.CTkEntry(
            pw_row, placeholder_text="Mínimo 4 caracteres",
            show="*", width=210, height=36
        )
        self.password_entry.pack(side="left", padx=(0, 6))
        
        self._icon_vis    = load_icon("visibility.png", size=(20,20))
        self._icon_vis_off = load_icon("visibility_off.png", size=(20,20))
        self._icon_back = load_icon("back_arrow.png", size=(16,16))
    
        
        self._toggle_btn = ctk.CTkButton(
            pw_row,
            text="",
            image=self._icon_vis_off,
            width=36, height=36,
            fg_color=theme.c("hover"), hover_color="#444444",
            command=self._toggle_visibility
        )
        self._toggle_btn.pack(side="left")

        ctk.CTkButton(
            self,
            text="Generar contraseña segura",
            image=load_icon("sync_green.png", 16),
            compound="left",
            fg_color=theme.CURRENT_THEME["accent"],
            command=self._generate_password
        ).pack(pady=(0, 14))
        # ── Confirm field ─────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Confirmar Password *",
                     font=theme.font(12), text_color=theme.c("text_secondary")).pack(anchor="center")

        conf_row = ctk.CTkFrame(self, fg_color="transparent")
        conf_row.pack(pady=(4, 20))

        self.confirm_entry = ctk.CTkEntry(
            conf_row, placeholder_text="Repetí la misma clave",
            show="*", width=210, height=36
        )
        self.confirm_entry.pack(side="left", padx=(0, 6))

        # Spacer to align with the toggle button above
        ctk.CTkFrame(conf_row, fg_color="transparent", width=36).pack(side="left")

        # ── Password generator ─────────────────────────────

        self._generator = PasswordGeneratorWidget(
            self,
            on_use=self._apply_generated_password
        )

        self._generator.pack(pady=(0, 18))
        # ── Status + submit ───────────────────────────────────────────────
        self.message_label = ctk.CTkLabel(self, text="")
        self.message_label.pack(pady=(0, 6))

        ctk.CTkButton(
            self, text="Crear Bóveda",
            image=load_icon("copy_white.png", size=(16,16)),  # files_icon no disponible
            compound="left",
            width=200, height=38,
            command=self.on_submit
        ).pack()

    def _apply_generated_password(self, password: str):
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)

        self.confirm_entry.delete(0, "end")
        self.confirm_entry.insert(0, password)

        self.show_message("Contraseña generada y copiada")
    
    def _toggle_visibility(self):
        self._pw_visible = not self._pw_visible
        show = "" if self._pw_visible else "*"
        self.password_entry.configure(show=show)
        self.confirm_entry.configure(show=show)
        icon = self._icon_vis if self._pw_visible else self._icon_vis_off
        self._toggle_btn.configure(image=icon, text="")

    def on_submit(self):
        p1 = self.password_entry.get()
        p2 = self.confirm_entry.get()
        if len(p1) < 10:
            self.show_message("La clave debe tener al menos 10 caracteres.", "error")
        elif p1 != p2:
            self.show_message("Las claves no coinciden.", "error")
        else:
            self.controller.handle_setup(p1)

    def show_message(self, text, msg_type="info"):
        color = "#ff4d4d" if msg_type == "error" else theme.c("accent")
        self.message_label.configure(text=text, text_color=color)