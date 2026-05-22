#!/bin/bash

echo "======================================"
echo " Bienvenido al instalador de CryptoVault"
echo "======================================"
echo ""

# 1. Preguntar dónde guardar los archivos .data
read -p "¿Dónde quieres que se guarden tus bóvedas por defecto? [Predeterminado: ~/.cryptovault_data]: " USER_PATH

# Si el usuario presiona Enter sin escribir nada, usamos el predeterminado
if [ -z "$USER_PATH" ]; then
    USER_PATH="~/.cryptovault_data"
fi

# Convertir el símbolo '~' a la ruta real (/home/usuario)
EVALUATED_PATH="${USER_PATH/#\~/$HOME}"

# Crear la carpeta y guardar la configuración
mkdir -p "$EVALUATED_PATH"
echo "$EVALUATED_PATH" > ~/.cryptovault_config
echo "✅ Directorio de datos configurado en: $EVALUATED_PATH"

# 2. Mover el ejecutable a la carpeta de aplicaciones del usuario
# 2. Mover el ejecutable a la carpeta de aplicaciones del usuario
mkdir -p ~/.local/bin

# Buscar si el archivo está suelto (ZIP) o dentro de dist/ (Desarrollo)
if [ -f "CryptoVault" ]; then
    cp CryptoVault ~/.local/bin/CryptoVault
elif [ -f "dist/CryptoVault" ]; then
    cp dist/CryptoVault ~/.local/bin/CryptoVault
else
    echo "❌ ERROR: No se encontró el programa CryptoVault. Asegúrate de compilarlo primero."
    exit 1
fi

chmod +x ~/.local/bin/CryptoVault
echo "✅ Ejecutable instalado en ~/.local/bin/CryptoVault"

# (Opcional) Copiar el icono si tienes uno. Si tienes un logo.png en tu proyecto, descomenta la siguiente línea:
# mkdir -p ~/.local/share/icons && cp logo.png ~/.local/share/icons/cryptovault.png

# 3. Crear el acceso directo para el buscador de Ubuntu
mkdir -p ~/.local/share/applications
cat <<EOF > ~/.local/share/applications/cryptovault.desktop
[Desktop Entry]
Name=CryptoVault
Comment=Tu gestor de contraseñas cifrado
Exec=$HOME/.local/bin/CryptoVault
Icon=utilities-terminal
Type=Application
Terminal=false
Categories=Utility;Security;
EOF

# Actualizar el buscador de Ubuntu para que detecte la nueva app
update-desktop-database ~/.local/share/applications

echo ""
echo "🎉 ¡Instalación completada con éxito!"
echo "Ahora puedes buscar 'CryptoVault' en el menú de aplicaciones de Ubuntu."