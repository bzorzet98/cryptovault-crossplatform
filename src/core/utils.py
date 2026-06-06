# src/core/utils.py
import sys
import os
import json
from types import SimpleNamespace

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Anchors to the 'src' directory during development.
    """
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller temporary folder
            base_path = sys._MEIPASS
        else:
            # 1. Get the directory where this file (utils.py) is located: src/core/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.abspath(os.path.join(current_dir, ".."))
    except Exception as e:
        print(f"Error determining resource path: {e}")
        base_path = os.path.abspath(".")  # Fallback to current directory
    return os.path.join(base_path, relative_path)


def load_theme(theme_name="dark"):
    path = get_resource_path(f"assets/themes/{theme_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # This trick converts the dictionary into an object
    # so you can use theme.colors.bg instead of theme["colors"]["bg"]
    return json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))