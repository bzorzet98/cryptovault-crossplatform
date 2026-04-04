import os

class StorageManager:
    """
    Handles saving and loading encrypted data from the local file system.
    """

    @staticmethod
    def save_vault(encrypted_data: str, filename: str = "vault.data"):
        """
        Writes the encrypted base64 string into a local file.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
        except Exception as e:
            raise IOError(f"Could not save the vault file: {e}")

    @staticmethod
    def load_vault(filename: str = "vault.data") -> str:
        """
        Reads the encrypted base64 string from the local file.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The vault file '{filename}' does not exist.")
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Could not read the vault file: {e}")