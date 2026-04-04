import os
import pytest
from src.core.models import Vault, Entity
from src.core.crypto import CryptoManager
from src.core.storage import StorageManager

def test_full_save_load_cycle():
    """
    Integration Test: Verifies the full flow from creating a vault 
    to saving it to disk and loading it back.
    """
    # 1. Arrange
    test_file = "test_vault.data"
    password = "master_password_2026"
    vault = Vault(user_id="pablo_dev")
    vault.entities.append(Entity(name="Netflix"))
    
    # 2. Act: Encrypt and Save
    encrypted_str = CryptoManager.encrypt(vault.to_dict(), password)
    StorageManager.save_vault(encrypted_str, filename=test_file)
    
    # 3. Act: Load and Decrypt
    loaded_str = StorageManager.load_vault(filename=test_file)
    decrypted_dict = CryptoManager.decrypt(loaded_str, password)
    
    # 4. Assert
    assert decrypted_dict["user_id"] == "pablo_dev"
    assert decrypted_dict["entities"][0]["name"] == "Netflix"
    
    # Clean up: Remove the test file after the test
    if os.path.exists(test_file):
        os.remove(test_file)