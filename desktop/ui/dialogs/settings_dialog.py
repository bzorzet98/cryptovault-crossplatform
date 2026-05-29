import customtkinter as ctk
import desktop.ui.themes.theme as theme

class SettingsDialog(ctk.CTkToplevel):

    def __init__(self, master, on_apply):

        super().__init__(master)

        self.on_apply = on_apply

        self.title("Preferencias")

        self.geometry("560x620")

        self.resizable(False, False)

        self.configure(
            fg_color=theme.c("bg")
        )

        self.after(10, lambda: self.grab_set())

        # ═══════════════════════════════════════════════
        # TITLE
        # ═══════════════════════════════════════════════

        ctk.CTkLabel(
            self,
            text="Configuración de interfaz",
            font=theme.font(22, "bold")
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            self,
            text="Personalizá la apariencia de CryptoVault",
            text_color=theme.c("grey"),
            font=theme.font(12)
        ).pack(pady=(0, 20))

        # ═══════════════════════════════════════════════
        # MAIN CONTAINER
        # ═══════════════════════════════════════════════
        container = ctk.CTkFrame(
            self,
            fg_color=theme.c("card"),
            corner_radius=12
        )

        container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )

        container.pack_propagate(False)
        

        # ═══════════════════════════════════════════════
        # THEME
        # ═══════════════════════════════════════════════

        ctk.CTkLabel(
            container,
            text="Tema",
            font=theme.font(15, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 6))

        self.theme_menu = ctk.CTkOptionMenu(
            container,
            values=["dark", "light", "oled"],
            width=220,
            height=34
        )

        self.theme_menu.set(
            theme.CURRENT_THEME
        )

        self.theme_menu.pack(
            anchor="w",
            padx=20
        )

        # ═══════════════════════════════════════════════
        # UI SCALE
        # ═══════════════════════════════════════════════

        ctk.CTkLabel(
            container,
            text="Escala de interfaz",
            font=theme.font(15, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 6))

        self.scale_value = ctk.StringVar(
            value=f"{theme.UI_SCALE:.2f}"
        )

        scale_row = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        scale_row.pack(
            fill="x",
            padx=20
        )

        self.scale_slider = ctk.CTkSlider(
            scale_row,
            from_=0.8,
            to=2.0,
            number_of_steps=12,
            command=self._on_scale_change
        )

        self.scale_slider.set(
            theme.UI_SCALE
        )

        self.scale_slider.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.scale_label = ctk.CTkLabel(
            scale_row,
            textvariable=self.scale_value,
            width=50,
            font=theme.font(12, "bold")
        )

        self.scale_label.pack(
            side="left",
            padx=(10, 0)
        )

        # ═══════════════════════════════════════════════
        # FONT SIZE
        # ═══════════════════════════════════════════════

        ctk.CTkLabel(
            container,
            text="Tamaño de texto",
            font=theme.font(15, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 6))

        self.font_menu = ctk.CTkOptionMenu(
            container,
            values=[
                "0.9",
                "1.0",
                "1.1",
                "1.2",
                "1.3"
            ],
            width=220,
            height=34
        )

        self.font_menu.set("1.0")

        self.font_menu.pack(
            anchor="w",
            padx=20
        )

        # ═══════════════════════════════════════════════
        # PREVIEW
        # ═══════════════════════════════════════════════

        ctk.CTkLabel(
            container,
            text="Vista previa",
            font=theme.font(15, "bold")
        ).pack(anchor="w", padx=20, pady=(24, 8))

        preview = ctk.CTkFrame(
            container,
            fg_color=theme.c("sidebar"),
            height=65,
            corner_radius=10
        )

        preview.pack(
            fill="x",
            padx=20,
            pady=(0, 16)
        )

        preview.pack_propagate(False)

        ctk.CTkLabel(
            preview,
            text="CryptoVault Preview",
            font=theme.font(18, "bold")
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            preview,
            text="Así se verá la interfaz",
            text_color=theme.c("grey"),
            font=theme.font(12)
        ).pack()

        # ═══════════════════════════════════════════════
        # BUTTONS
        # ═══════════════════════════════════════════════

        btns = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        btns.pack(
            pady=(0, 18)
        )

        ctk.CTkButton(
            btns,
            text="Aplicar",
            width=140,
            height=38,
            fg_color=theme.c("accent"),
            hover_color="#1e5c3d",
            command=self._apply
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ctk.CTkButton(
            btns,
            text="Cancelar",
            width=120,
            height=38,
            fg_color="#444444",
            hover_color="#333333",
            command=self.destroy
        ).pack(side="left")

    # ═══════════════════════════════════════════════
    # EVENTS
    # ═══════════════════════════════════════════════

    def _on_scale_change(self, value):

        self.scale_value.set(
            f"{float(value):.2f}"
        )

    def _apply(self):

        theme.set_theme(
            self.theme_menu.get()
        )

        theme.set_scale(
            float(self.scale_slider.get())
        )

        self.on_apply()

        self.destroy()