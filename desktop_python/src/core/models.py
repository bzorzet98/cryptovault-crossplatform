"""
CryptoVault — Data Models (v2)

Vault
 └─ tabs: List[Tab]
     └─ credentials: List[Credential]
         └─ fields: dict[key, value]          ← default fields for the tab
         └─ extra_fields: List[ExtraField]     ← user-added fields

System tabs (is_system=True) cannot be deleted.
The "deleted" tab is special: credentials carry a deleted_at timestamp
and are auto-purged after TRASH_TTL_DAYS days.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any

TRASH_TTL_DAYS = 60

# ── Default tab definitions ────────────────────────────────────────────────────

SYSTEM_TABS: list[dict] = [
    {
        "id": "system_banks",
        "name": "Bancos",
        "icon": "🏦",
        "is_system": True,
        "default_fields": [
            {"key": "email",    "label": "Email",                 "secret": False},
            {"key": "pin",      "label": "Clave PIN",             "secret": True},
            {"key": "pil",      "label": "Clave PIL",             "secret": True},
            {"key": "alfa",     "label": "Clave Alfanumérica",    "secret": True},
            {"key": "user_hb",  "label": "Usuario Homebanking",   "secret": False},
            {"key": "pass_hb",  "label": "Clave Homebanking",     "secret": True},
        ],
        "credentials": [],
    },
    {
        "id": "system_emails",
        "name": "Emails",
        "icon": "📧",
        "is_system": True,
        "default_fields": [
            {"key": "email",       "label": "Dirección Email",    "secret": False},
            {"key": "password",    "label": "Contraseña",         "secret": True},
            {"key": "recovery",    "label": "Email de recuperación", "secret": False},
            {"key": "phone",       "label": "Teléfono asociado",  "secret": False},
        ],
        "credentials": [],
    },
    {
        "id": "system_streaming",
        "name": "Plataformas",
        "icon": "🎬",
        "is_system": True,
        "default_fields": [
            {"key": "email",    "label": "Email / Usuario",   "secret": False},
            {"key": "password", "label": "Contraseña",        "secret": True},
            {"key": "plan",     "label": "Plan contratado",   "secret": False},
            {"key": "payment",  "label": "Método de pago",    "secret": False},
        ],
        "credentials": [],
    },
    {
        "id": "system_social",
        "name": "Redes Sociales",
        "icon": "🛡️",
        "is_system": True,
        "default_fields": [
            {"key": "username", "label": "Usuario / Handle",  "secret": False},
            {"key": "email",    "label": "Email asociado",    "secret": False},
            {"key": "password", "label": "Contraseña",        "secret": True},
            {"key": "2fa",      "label": "Código 2FA / App",  "secret": True},
        ],
        "credentials": [],
    },
    {
        "id": "system_trash",
        "name": "Eliminados",
        "icon": "🗑️",
        "is_system": True,
        "is_trash": True,
        "default_fields": [],
        "credentials": [],
    },
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_vault() -> dict:
    """Returns a brand-new vault dict ready to be encrypted."""
    import copy
    return {"tabs": copy.deepcopy(SYSTEM_TABS)}


# ── Vault mutation helpers (all operate on the plain dict) ─────────────────────

def get_tab(vault: dict, tab_id: str) -> dict | None:
    for t in vault["tabs"]:
        if t["id"] == tab_id:
            return t
    return None


def get_trash_tab(vault: dict) -> dict:
    for t in vault["tabs"]:
        if t.get("is_trash"):
            return t
    raise KeyError("Trash tab not found")


def purge_old_trash(vault: dict) -> None:
    """Remove trashed credentials older than TRASH_TTL_DAYS."""
    from datetime import timedelta
    trash = get_trash_tab(vault)
    cutoff = datetime.now(timezone.utc) - timedelta(days=TRASH_TTL_DAYS)
    trash["credentials"] = [
        c for c in trash["credentials"]
        if datetime.fromisoformat(c.get("deleted_at", now_iso())) > cutoff
    ]


def add_tab(vault: dict, name: str, icon: str, default_fields: list[dict]) -> dict:
    """Creates a new user tab and appends it before the trash tab."""
    tab = {
        "id": new_id(),
        "name": name,
        "icon": icon,
        "is_system": False,
        "default_fields": default_fields,
        "credentials": [],
    }
    # Insert before trash (always last)
    trash_idx = next(
        (i for i, t in enumerate(vault["tabs"]) if t.get("is_trash")), len(vault["tabs"])
    )
    vault["tabs"].insert(trash_idx, tab)
    return tab


def add_credential(vault: dict, tab_id: str, name: str,
                   fields: dict[str, str], extra_fields: list[dict]) -> dict:
    """Adds a new credential to the given tab."""
    tab = get_tab(vault, tab_id)
    if tab is None:
        raise ValueError(f"Tab {tab_id} not found")
    cred = {
        "id": new_id(),
        "name": name,
        "fields": fields,
        "extra_fields": extra_fields,   # [{"key":..., "label":..., "secret":..., "value":...}]
        "deleted_at": None,
        "original_tab_id": None,
    }
    tab["credentials"].append(cred)
    return cred


def update_credential(vault: dict, tab_id: str, cred_id: str,
                      name: str, fields: dict, extra_fields: list) -> None:
    tab = get_tab(vault, tab_id)
    if tab is None:
        raise ValueError(f"Tab {tab_id} not found")
    for cred in tab["credentials"]:
        if cred["id"] == cred_id:
            cred["name"]         = name
            cred["fields"]       = fields
            cred["extra_fields"] = extra_fields
            return
    raise ValueError(f"Credential {cred_id} not found")


def soft_delete_credential(vault: dict, tab_id: str, cred_id: str) -> None:
    """Moves credential to trash tab with a timestamp."""
    tab = get_tab(vault, tab_id)
    if tab is None:
        return
    for i, cred in enumerate(tab["credentials"]):
        if cred["id"] == cred_id:
            tab["credentials"].pop(i)
            cred["deleted_at"]      = now_iso()
            cred["original_tab_id"] = tab_id
            get_trash_tab(vault)["credentials"].append(cred)
            return


def restore_credential(vault: dict, cred_id: str) -> None:
    """Moves credential from trash back to its original tab (or first non-trash tab)."""
    trash = get_trash_tab(vault)
    for i, cred in enumerate(trash["credentials"]):
        if cred["id"] == cred_id:
            trash["credentials"].pop(i)
            cred["deleted_at"] = None
            dest_id = cred.get("original_tab_id")
            dest    = get_tab(vault, dest_id) if dest_id else None
            if dest is None:
                dest = next(t for t in vault["tabs"] if not t.get("is_trash"))
            cred["original_tab_id"] = None
            dest["credentials"].append(cred)
            return


def hard_delete_credential(vault: dict, cred_id: str) -> None:
    """Permanently removes a credential from the trash tab."""
    trash = get_trash_tab(vault)
    trash["credentials"] = [c for c in trash["credentials"] if c["id"] != cred_id]


def delete_tab(vault: dict, tab_id: str) -> None:
    """Deletes a user-created tab (moves its credentials to trash first)."""
    tab = get_tab(vault, tab_id)
    if tab is None or tab.get("is_system"):
        raise ValueError("Cannot delete a system tab")
    for cred in tab["credentials"]:
        cred["deleted_at"]      = now_iso()
        cred["original_tab_id"] = tab_id
        get_trash_tab(vault)["credentials"].append(cred)
    vault["tabs"] = [t for t in vault["tabs"] if t["id"] != tab_id]