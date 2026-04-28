"""
vault_schema.py
───────────────
Single source of truth for the vault data model.

Vault JSON structure:
{
    "version": 2,
    "tabs": [
        {
            "id": str (uuid4),
            "name": str,
            "icon": str (emoji),
            "is_system": bool,
            "default_fields": [
                {"key": str, "label": str, "secret": bool}
            ],
            "credentials": [
                {
                    "id": str (uuid4),
                    "name": str,
                    "fields": {key: value, ...},
                    "extra_fields": [
                        {"key": str, "label": str, "secret": bool, "value": str}
                    ],
                    "deleted_at": null | ISO-8601 str
                }
            ]
        }
    ]
}
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

# ── Emoji palette offered in the icon picker ──────────────────────────────────
ICON_OPTIONS = [
    "🏦", "📧", "🎬", "🛡️", "🗑️", "💼", "🎮", "🛒", "🏥", "📚",
    "✈️",  "🏠", "💳", "🔑", "🌐", "📱", "💡", "🎵", "📷", "🤖",
    "🧪", "🏋️", "🎓", "🍕", "🚗", "👾", "🧩", "💰", "📝", "⭐",
]

DELETED_TAB_ID  = "__deleted__"
DELETED_PURGE_DAYS = 60


# ── Default field definitions per system tab ──────────────────────────────────

_BANK_FIELDS = [
    {"key": "email",   "label": "Email",                 "secret": False},
    {"key": "pin",     "label": "Clave PIN",              "secret": True},
    {"key": "pil",     "label": "Clave PIL",              "secret": True},
    {"key": "alfa",    "label": "Clave Alfanumérica",     "secret": True},
    {"key": "user_hb", "label": "Usuario Homebanking",    "secret": False},
    {"key": "pass_hb", "label": "Clave Homebanking",      "secret": True},
]

_EMAIL_FIELDS = [
    {"key": "email",        "label": "Dirección Email",   "secret": False},
    {"key": "password",     "label": "Contraseña",        "secret": True},
    {"key": "recovery",     "label": "Email de Recuperación", "secret": False},
    {"key": "phone",        "label": "Teléfono asociado", "secret": False},
]

_PLATFORM_FIELDS = [
    {"key": "email",    "label": "Email / Usuario",  "secret": False},
    {"key": "password", "label": "Contraseña",       "secret": True},
    {"key": "plan",     "label": "Plan / Suscripción","secret": False},
]

_SOCIAL_FIELDS = [
    {"key": "username", "label": "Usuario",     "secret": False},
    {"key": "email",    "label": "Email",        "secret": False},
    {"key": "password", "label": "Contraseña",  "secret": True},
    {"key": "phone",    "label": "Teléfono 2FA", "secret": False},
]

_WORK_FIELDS = [
    {"key": "service",  "label": "Servicio / Sistema", "secret": False},
    {"key": "username", "label": "Usuario",             "secret": False},
    {"key": "password", "label": "Contraseña",          "secret": True},
    {"key": "url",      "label": "URL / Servidor",      "secret": False},
    {"key": "notes",    "label": "Notas",               "secret": False},
]


def _make_system_tab(tab_id: str, name: str, icon: str, fields: list) -> dict:
    return {
        "id":             tab_id,
        "name":           name,
        "icon":           icon,
        "is_system":      True,
        "default_fields": [f.copy() for f in fields],
        "credentials":    [],
    }


def build_default_vault() -> dict:
    """Returns a fresh vault dict with all system tabs and empty credentials."""
    return {
        "version": 2,
        "tabs": [
            _make_system_tab("__banks__",     "Bancos",               "🏦", _BANK_FIELDS),
            _make_system_tab("__emails__",    "Emails",               "📧", _EMAIL_FIELDS),
            _make_system_tab("__platforms__", "Plataformas Digitales","🎬", _PLATFORM_FIELDS),
            _make_system_tab("__social__",    "Redes Sociales",       "🛡️", _SOCIAL_FIELDS),
            _make_system_tab("__work__",      "Trabajo",    "💼", _WORK_FIELDS),
            # Deleted tab — special, always last
            {
                "id":             DELETED_TAB_ID,
                "name":           "Eliminados",
                "icon":           "🗑️",
                "is_system":      True,
                "default_fields": [],
                "credentials":    [],
            },
        ],
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())


def new_credential(name: str, fields: dict, extra_fields: list | None = None) -> dict:
    return {
        "id":           new_id(),
        "name":         name,
        "fields":       fields,
        "extra_fields": extra_fields or [],
        "deleted_at":   None,
    }


def new_user_tab(name: str, icon: str, default_fields: list) -> dict:
    return {
        "id":             new_id(),
        "name":           name,
        "icon":           icon,
        "is_system":      False,
        "default_fields": default_fields,
        "credentials":    [],
    }


def purge_old_deleted(vault: dict) -> bool:
    """
    Removes credentials in the Deleted tab older than DELETED_PURGE_DAYS.
    Returns True if anything was purged.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=DELETED_PURGE_DAYS)
    deleted_tab = get_tab(vault, DELETED_TAB_ID)
    if not deleted_tab:
        return False

    before = len(deleted_tab["credentials"])
    deleted_tab["credentials"] = [
        c for c in deleted_tab["credentials"]
        if _parse_dt(c.get("deleted_at")) > cutoff
    ]
    return len(deleted_tab["credentials"]) < before


def get_tab(vault: dict, tab_id: str) -> dict | None:
    for t in vault.get("tabs", []):
        if t["id"] == tab_id:
            return t
    return None


def _parse_dt(iso: str | None) -> datetime:
    if not iso:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(iso)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()