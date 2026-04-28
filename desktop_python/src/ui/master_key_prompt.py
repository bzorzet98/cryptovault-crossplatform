"""
master_key_prompt.py
─────────────────────
A modal Toplevel that asks the user to re-enter the Master Password
before revealing sensitive credential fields.

Usage:
    MasterKeyPrompt(
        parent   = self,                          # any tk widget
        verify   = lambda pw: pw == master_key,   # callable → bool
        on_ok    = lambda: self._do_reveal(),      # called if verified
        on_cancel= lambda: None                    # optional
    )
"""

import customtkinter as ctk

_BG     = "#1e1e1e"
_ACCENT = "#2c8558"
_RED    = "#a33030"


class MasterKeyPrompt(ctk.CTkToplevel):
    """
    Parameters
    ----------
    parent    : tk widget — owner window
    verify    : callable(password: str) → bool
    on_ok     : callable() — invoked after successful verification
    on_cancel : callable() — invoked on cancel / wrong password dismissed
    """

    def __init__(self, parent, verify, on_ok, on_cancel=None):
        super().__init__(parent)
        self.verify    = verify
        self.on_ok     = on_ok
        self.on_cancel = on_cancel or (lambda: None)

        self._pw_visible = False

        # ── Window setup ──────────────────────────────────────────────────
        self.title("Verificar identidad")
        self.geometry("340x220")
        self.resizable(False, False)
        self.grab_set()           # modal
        self.focus_force()
        self.configure(fg_color=_BG)

        # ── Content ───────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="🔐  Verificación requerida",
            font=("Roboto", 16, "bold")
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            self,
            text="Ingresá tu Master Password\npara ver los datos cifrados.",
            font=("Roboto", 12), text_color="#888888", justify="center"
        ).pack(pady=(0, 16))

        # Password row
        pw_row = ctk.CTkFrame(self, fg_color="transparent")
        pw_row.pack(pady=(0, 6))

        self._entry = ctk.CTkEntry(
            pw_row, placeholder_text="Master Password",
            show="*", width=210, height=36
        )
        self._entry.pack(side="left", padx=(0, 6))
        self._entry.bind("<Return>", lambda e: self._submit())
        self._entry.focus_set()

        self._eye_btn = ctk.CTkButton(
            pw_row, text="👁", width=36, height=36,
            fg_color="#333333", hover_color="#444444",
            command=self._toggle_visibility
        )
        self._eye_btn.pack(side="left")

        # Error message
        self._msg = ctk.CTkLabel(self, text="", font=("Roboto", 11))
        self._msg.pack(pady=(0, 10))

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="Confirmar", width=110, height=34,
            fg_color=_ACCENT, hover_color="#1e5c3d",
            command=self._submit
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Cancelar", width=90, height=34,
            fg_color="#444444", hover_color="#333333",
            command=self._cancel
        ).pack(side="left")

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    # ── Actions ───────────────────────────────────────────────────────────

    def _toggle_visibility(self):
        self._pw_visible = not self._pw_visible
        self._entry.configure(show="" if self._pw_visible else "*")
        self._eye_btn.configure(text="🙈" if self._pw_visible else "👁")

    def _submit(self):
        pw = self._entry.get()
        if self.verify(pw):
            self.grab_release()
            self.destroy()
            self.on_ok()
        else:
            self._msg.configure(text="Contraseña incorrecta.", text_color=_RED)
            self._entry.delete(0, "end")
            self._entry.focus_set()

    def _cancel(self):
        self.grab_release()
        self.destroy()
        self.on_cancel()