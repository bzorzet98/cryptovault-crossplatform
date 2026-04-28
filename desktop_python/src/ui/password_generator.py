"""
password_generator.py
──────────────────────
Utility functions + a small inline widget used inside AddCredentialPanel
and CredentialCard edit mode.

generate_password(length, upper, lower, digits, symbols) → str
PasswordGeneratorWidget  — inline CTkFrame with options + output
"""

import random
import string
import customtkinter as ctk

_BG     = "#1a1a1a"
_ACCENT = "#2c8558"
_GREY   = "#888888"


# ── Pure utility ─────────────────────────────────────────────────────────────

def generate_password(
    length:  int  = 16,
    upper:   bool = True,
    lower:   bool = True,
    digits:  bool = True,
    symbols: bool = False,
) -> str:
    """
    Generates a cryptographically random password.
    Guarantees at least one character from each enabled category.
    """
    pool = ""
    required = []

    if upper:
        pool += string.ascii_uppercase
        required.append(random.choice(string.ascii_uppercase))
    if lower:
        pool += string.ascii_lowercase
        required.append(random.choice(string.ascii_lowercase))
    if digits:
        pool += string.digits
        required.append(random.choice(string.digits))
    if symbols:
        syms = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        pool += syms
        required.append(random.choice(syms))

    if not pool:
        pool = string.ascii_letters + string.digits

    remaining = [random.choice(pool) for _ in range(length - len(required))]
    password  = required + remaining
    random.shuffle(password)
    return "".join(password)


# ── Inline widget ─────────────────────────────────────────────────────────────

class PasswordGeneratorWidget(ctk.CTkFrame):
    """
    Compact generator that lives inside a form panel.

    Parameters
    ----------
    master       : parent frame
    on_use       : callable(password: str) — called when user clicks "Usar"
    """

    def __init__(self, master, on_use):
        super().__init__(master, fg_color=_BG, corner_radius=8)
        self.on_use = on_use

        # ── Options row ───────────────────────────────────────────────────
        opts = ctk.CTkFrame(self, fg_color="transparent")
        opts.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(opts, text="Generar contraseña:",
                     font=("Roboto", 12), text_color=_GREY).pack(side="left", padx=(0, 10))

        self._upper_var   = ctk.BooleanVar(value=True)
        self._lower_var   = ctk.BooleanVar(value=True)
        self._digits_var  = ctk.BooleanVar(value=True)
        self._symbols_var = ctk.BooleanVar(value=False)
        self._length_var  = ctk.IntVar(value=16)

        for text, var in [("A-Z", self._upper_var), ("a-z", self._lower_var),
                          ("0-9", self._digits_var), ("!@#", self._symbols_var)]:
            ctk.CTkCheckBox(opts, text=text, variable=var,
                            width=55, font=("Roboto", 11),
                            command=self._regenerate).pack(side="left", padx=2)

        # Length slider
        ctk.CTkLabel(opts, text="Largo:", font=("Roboto", 11),
                     text_color=_GREY).pack(side="left", padx=(8, 2))

        self._len_label = ctk.CTkLabel(opts, text="16",
                                       font=("Roboto", 11, "bold"), width=24)
        self._len_label.pack(side="left")

        ctk.CTkSlider(
            opts, from_=8, to=32, number_of_steps=24,
            variable=self._length_var, width=80,
            command=self._on_slider
        ).pack(side="left", padx=(2, 0))

        # ── Output row ────────────────────────────────────────────────────
        out_row = ctk.CTkFrame(self, fg_color="transparent")
        out_row.pack(fill="x", padx=10, pady=(0, 8))

        self._pw_var = ctk.StringVar()
        self._pw_entry = ctk.CTkEntry(
            out_row, textvariable=self._pw_var,
            width=220, height=32, font=("Roboto", 12),
            state="normal"
        )
        self._pw_entry.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            out_row, text="↻", width=32, height=32,
            fg_color="#333333", hover_color="#444444",
            font=("Roboto", 16),
            command=self._regenerate
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            out_row, text="Usar", width=60, height=32,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._use
        ).pack(side="left")

        self._regenerate()

    # ── Helpers ───────────────────────────────────────────────────────────

    def _on_slider(self, value):
        length = int(value)
        self._length_var.set(length)
        self._len_label.configure(text=str(length))
        self._regenerate()

    def _regenerate(self):
        pw = generate_password(
            length  = self._length_var.get(),
            upper   = self._upper_var.get(),
            lower   = self._lower_var.get(),
            digits  = self._digits_var.get(),
            symbols = self._symbols_var.get(),
        )
        self._pw_var.set(pw)

    def _use(self):
        self.on_use(self._pw_var.get())