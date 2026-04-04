import pytest
from src.core.models import Vault, Entity, Credential
from src.core.crypto import CryptoManager

def test_encryption_decryption_cycle():
    """
    Happy Path: Verify that a Vault can be encrypted and decrypted 
    returning the exact same data.
    """
    # 1. Arrange: Create a real Vault scenario
    password = "super-secret-password"
    original_vault = Vault(user_id="user_v1")
    
    bank = Entity(name="Global Bank")
    acc = Credential(alias="Savings", username="pablo_dev", password="123")
    acc.add_extra_field("PIN", "9876")
    acc.add_extra_field("PIL", "ABC")
    
    bank.credentials.append(acc)
    original_vault.entities.append(bank)
    
    # 2. Act: Convert to dict, Encrypt, and then Decrypt
    vault_dict = original_vault.to_dict()
    encrypted_base64 = CryptoManager.encrypt(vault_dict, password)
    
    # Ensure the encrypted data is a string (Base64) and not plain text
    assert isinstance(encrypted_base64, str)
    assert "Global Bank" not in encrypted_base64
    
    decrypted_dict = CryptoManager.decrypt(encrypted_base64, password)
    
    # 3. Assert: Check if data is identical
    assert decrypted_dict["user_id"] == "user_v1"
    assert decrypted_dict["entities"][0]["name"] == "Global Bank"
    assert decrypted_dict["entities"][0]["credentials"][0]["extra_fields"]["PIN"] == "9876"

def test_wrong_password_fails():
    """
    Sad Path: Ensure that using a different password raises a ValueError.
    """
    # Arrange
    data = {"secret": "my private keys"}
    correct_pw = "secure_pass_123"
    wrong_pw = "wrong_pass_456"
    
    # Act
    encrypted = CryptoManager.encrypt(data, correct_pw)
    
    # Assert: It must raise our custom ValueError
    with pytest.raises(ValueError, match="Decryption failed"):
        CryptoManager.decrypt(encrypted, wrong_pw)

def test_cipher_uniqueness():
    """
    Security Test: Encrypting the same data twice should produce 
    different results (due to random Salt and Nonce).
    """
    data = {"data": "confidential"}
    pw = "password"
    
    cipher1 = CryptoManager.encrypt(data, pw)
    cipher2 = CryptoManager.encrypt(data, pw)
    
    # Assert: Ciphers must be different to prevent pattern analysis
    assert cipher1 != cipher2