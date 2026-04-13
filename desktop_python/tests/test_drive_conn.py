from src.core.drive_manager import DriveManager

try:
    print("Iniciando autenticación...")
    dm = DriveManager(credentials_path='desktop_python/credentials.json', 
                      token_path='desktop_python/token.json')
    print("¡Autenticación exitosa!")
except Exception as e:
    print(f"Error: {e}")
    