from pathlib import Path
import sys


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path.cwd()

    return base_path / relative_path