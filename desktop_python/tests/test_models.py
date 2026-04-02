import pytest
from src.core.models import Credential, Entity, Vault

def test_bank_with_multiple_keys():
    """
    Test a real-world scenario: A bank account with PIN, PIL, and Token.
    """
    bank_cred = Credential(alias="Main Account", username="pablo_user")
    
    # Adding multiple bank keys
    bank_cred.add_extra_field("PIN", "1234")
    bank_cred.add_extra_field("PIL", "ABC")
    bank_cred.add_extra_field("Token Key", "998877")
    
    assert len(bank_cred.extra_fields) == 3
    assert bank_cred.extra_fields["PIL"] == "ABC"

def test_duplicate_label_error():
    """
    Ensure the system prevents overwriting labels by accident.
    """
    cred = Credential()
    cred.add_extra_field("Recovery Email", "test@mail.com")
    
    with pytest.raises(ValueError):
        cred.add_extra_field("Recovery Email", "other@mail.com")

def test_vault_serialization():
    """
    Ensure the Vault can be converted to a dictionary correctly.
    This is essential for the encryption process later.
    """
    vault = Vault(user_id="user_123")
    entity = Entity(name="Google")
    vault.entities.append(entity)
    
    vault_dict = vault.to_dict()
    assert vault_dict["user_id"] == "user_123"
    assert vault_dict["entities"][0]["name"] == "Google"