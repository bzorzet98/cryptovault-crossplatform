import os
from src.core.models import Vault, Entity, Credential
from src.core.crypto import CryptoManager
from src.core.storage import StorageManager
from src.core.drive_manager import DriveManager

def test_sync_to_cloud():
    print("--- Iniciando Sincronización Completa ---")
    
    # 1. Crear datos de prueba
    vault = Vault(user_id="pablo_dev_cloud")
    vault.entities.append(Entity(name="Google Cloud Test"))
    
    # 2. Cifrar y Guardar Localmente
    password = "clave-secreta-123"
    filename = "vault.data"
    encrypted_str = CryptoManager.encrypt(vault.to_dict(), password)
    StorageManager.save_vault(encrypted_str, filename=filename)
    print(f"[OK] Archivo {filename} creado y cifrado localmente.")

    # 3. Subir a Google Drive
    try:
        # Nota: Asegúrate de que las rutas a los JSON sean correctas según tu carpeta
        dm = DriveManager(
            credentials_path='desktop_python/credentials.json', 
            token_path='desktop_python/token.json'
        )
        file_id = dm.upload_vault(filename)
        print(f"[OK] ¡Archivo subido a Drive con éxito! ID: {file_id}")
    except Exception as e:
        print(f"[ERROR] Falló la subida: {e}")

if __name__ == "__main__":
    test_sync_to_cloud()