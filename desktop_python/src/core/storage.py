import os

class StorageManager:
    """
    Handles saving and loading encrypted data from the local file system.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_vault(self, encrypted_data: str):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
        except Exception as e:
            raise IOError(f"Could not save the vault file at {self.file_path}: {e}")

    def load_vault(self) -> str:
        if not self.vault_exists():
            raise FileNotFoundError(f"The vault file '{self.file_path}' does not exist.")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Could not read the vault file at {self.file_path}: {e}")

    def vault_exists(self) -> bool:
        return os.path.exists(self.file_path)

    def get_path(self) -> str:
        return self.file_path

    def get_name_without_extension(self) -> str:
        """Returns filename without extension. Used by DashboardView title."""
        basename = os.path.basename(self.file_path)
        return basename.rsplit('.', 1)[0] if '.' in basename else basename