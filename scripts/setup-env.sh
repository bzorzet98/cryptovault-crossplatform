#!/usr/bin/env bash

# Detener el script si ocurre algún error
set -e

# 1. Detectar de forma segura la raíz del proyecto (un nivel arriba de este script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

ENV_NAME="cryptovault-env"
PYTHON_VERSION="3.12"

echo "=================================================="
echo "🚀 Iniciando la creación del entorno Conda..."
echo "=================================================="

# 2. Comprobar si conda está instalado
if ! command -v conda &> /dev/null; then
    echo "❌ Error: Conda no está instalado o no está en el PATH."
    exit 1
fi

# 3. Crear el entorno con Python 3.12 y pip incorporado
echo "📦 Creando entorno Conda '$ENV_NAME' con Python $PYTHON_VERSION..."
conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION" pip

# 4. Inicializar conda para el script de Bash y activar el entorno
eval "$(conda shell.bash hook)"
echo "🔄 Activando el entorno '$ENV_NAME'..."
conda activate "$ENV_NAME"

# 5. Movernos a la raíz real del proyecto
cd "$PROJECT_ROOT"

# 6. Instalar las dependencias desde requirements.txt
echo "📥 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

# 7. Exportar el estado exacto del entorno a requirements.txt en la raíz
echo "📄 Exportando requerimientos congelados a la raíz del proyecto..."
pip freeze > requirements.txt

echo "=================================================="
echo "✅ ¡Entorno configurado con éxito!"
echo "=================================================="
echo "Para activar tu nuevo entorno en la terminal, corre:"
echo "conda activate $ENV_NAME"
echo "=================================================="