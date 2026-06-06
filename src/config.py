# src/config.py
from src.core.utils import load_theme

# In the future, this string could come from a "settings" file
ACTIVE_THEME_NAME = "dark_mode" 

# Load the object
THEME = load_theme(ACTIVE_THEME_NAME)

