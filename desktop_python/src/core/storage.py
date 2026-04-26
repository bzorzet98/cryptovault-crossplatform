import os
import shutil

class StorageManager:
    """
    Handles saving and loading encrypted data from the local file system.
    """

    def __init__(self, file_path: str):
        """
        Initializes the manager with the absolute path where vault.data will live.
        """
        self.file_path = file_path

    def save_vault(self, encrypted_data: str):
        """
        Writes the encrypted base64 string into the local file.
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
        Checks if the vault file exists at the current absolute path.
        """
        return os.path.exists(self.file_path)

    def get_path(self) -> str:
        """
        Returns the absolute path. Used by the Orchestrator to pass to DriveManager.
        """
        return self.file_path

    def get_filename(self) -> str:
        """
        Returns just the filename (e.g. 'vault.data'), without the directory.
        """
        return os.path.basename(self.file_path)

    def get_name_without_extension(self) -> str:
        """
        Returns the vault name without the .data extension (e.g. 'vault').
        """
        return os.path.splitext(self.get_filename())[0]

    def rename_vault(self, new_name: str) -> str:
        """
        Renames the vault file on disk and updates the internal path.
        - new_name: just the base name, without extension (e.g. 'my_vault')
        - Returns the new absolute path.
        - Raises ValueError if a file with that name already exists.
        - Raises FileNotFoundError if the current vault doesn't exist yet.
        """
        # Sanitize: remove any extension the user might have typed
        clean_name = os.path.splitext(new_name.strip())[0]
        if not clean_name:
            raise ValueError("The vault name cannot be empty.")

        new_filename = f"{clean_name}.data"
        new_path = os.path.join(os.path.dirname(self.file_path), new_filename)

        if os.path.abspath(new_path) == os.path.abspath(self.file_path):
            # Same name, nothing to do
            return self.file_path

        if os.path.exists(new_path):
            raise ValueError(f"A vault named '{new_filename}' already exists.")

        if self.vault_exists():
            shutil.move(self.file_path, new_path)

        # Update internal state
        self.file_path = new_path
        return new_path