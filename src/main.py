# src/main.py
# Dentro de tu función route_change en main.py

def attempt_login(password):
    try:
        # Aquí llamas a tu CryptoManager y StorageManager
        encrypted_data = storage_manager.load_vault()
        decrypted_data = CryptoManager.decrypt(encrypted_data, password)
        
        # Si funciona, cambias de pantalla
        page.go("/dashboard")
    except ValueError:
        # Si falla (contraseña incorrecta), le avisas a la vista
        # Nota: Necesitarías mantener una referencia a la vista actual
        current_login_view.show_message("Credenciales incorrectas.", is_error=True)

def go_back():
    page.go("/") # O la ruta de la vista Welcome/Selector

# Instanciamos la vista pasando las funciones
login_view = LoginView(
    page=page, 
    on_login=attempt_login, 
    on_back=go_back
)