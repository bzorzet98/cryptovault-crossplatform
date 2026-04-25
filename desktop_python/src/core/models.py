from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import uuid

@dataclass
class Credential:
    """
    Represents an individual account (e.g., Homebanking, Gmail).
    It uses a dictionary for flexible extra information like PIN or PIL.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alias: str = ""
    username: str = ""
    password: str = ""
    extra_fields: Dict[str, str] = field(default_factory=dict)
    notes: Optional[str] = ""

    def add_extra_field(self, label: str, value: str, overwrite: bool = False):
        """
        Adds a new custom field. If the label exists, it raises a ValueError
        unless overwrite is set to True.
        """
        if label in self.extra_fields and not overwrite:
            raise ValueError(f"Label '{label}' already exists. Use overwrite=True.")
        self.extra_fields[label] = value

@dataclass
class Entity:
    """
    Groups multiple credentials under one organization (e.g., a Bank).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    credentials: List[Credential] = field(default_factory=list)

@dataclass
class Vault:
    """
    The main data structure that holds all entities and user information.
    """
    user_id: str
    entities: List[Entity] = field(default_factory=list)

    def to_dict(self):
        """Converts the entire Vault into a dictionary for JSON serialization."""
        return asdict(self)