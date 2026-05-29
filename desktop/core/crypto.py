import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    """
    Handles encryption and decryption using AES-256-GCM.
    It uses PBKDF2 for key derivation to ensure high security against brute force.
    """
    
    ITERATIONS = 600000  # OWASP recommended iterations for PBKDF2-SHA256
    KEY_SIZE = 32        # 256 bits for AES-256

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """
        Derives a secure 256-bit key from a password and a salt.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=CryptoManager.KEY_SIZE,
            salt=salt,
            iterations=CryptoManager.ITERATIONS,
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt(data_dict: dict, password: str) -> str:
        """
        Encrypts a dictionary and returns a base64 encoded string.
        Output format: salt(16b) + nonce(12b) + ciphertext/tag
        """
        # 1. Convert dict to JSON bytes
        json_data = json.dumps(data_dict).encode('utf-8')
        
        # 2. Generate random security values
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # 3. Derive key and encrypt
        key = CryptoManager._derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        # AESGCM.encrypt includes the authentication tag automatically
        ciphertext = aesgcm.encrypt(nonce, json_data, None)
        
        # 4. Combine all parts and encode to Base64 for storage
        combined = salt + nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_base64: str, password: str) -> dict:
        """
        Decrypts the base64 string and returns the original dictionary.
        Raises ValueError if the password is wrong or data is corrupted.
        """
        try:
            # 1. Decode from Base64
            combined = base64.b64decode(encrypted_base64)
            
            # 2. Extract components based on fixed sizes
            salt = combined[:16]
            nonce = combined[16:28]
            ciphertext = combined[28:]
            
            # 3. Derive key and decrypt
            key = CryptoManager._derive_key(password, salt)
            aesgcm = AESGCM(key)
            
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(decrypted_data.decode('utf-8'))
            
        except Exception as e:
            # We raise a generic error to avoid giving clues to an attacker
            raise ValueError("Decryption failed. Invalid password or corrupted data.") from e