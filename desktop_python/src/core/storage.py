import os

class StorageManager:
    """
    Handles saving and loading encrypted data from the local file system.
    """

    def __init__(self, file_path: str):
        """
        Inicializa el manager con la ruta absoluta donde vivirá el vault.data.
        """
        self.file_path = file_path

    def save_vault(self, encrypted_data: str):
        """
        Writes the encrypted base64 string into a local file.
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
        except Exception as e:
            raise IOError(f"Could not save the vault file at {self.file_path}: {e}")

    def load_vault(self) -> str:
        """
        Reads the encrypted base64 string from the local file.
        """
        if not self.vault_exists():
            raise FileNotFoundError(f"The vault file '{self.file_path}' does not exist.")
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Could not read the vault file at {self.file_path}: {e}")

    def vault_exists(self) -> bool:
        """
        Checks if the vault file exists in the specific absolute path.
        """
        return os.path.exists(self.file_path)

    def get_path(self) -> str:
        """
        Returns the absolute path. Used by the Orchestrator to pass to DriveManager.
        """
        return self.file_path