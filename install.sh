#!/bin/bash

# Installation script for Floating VSCode Opener

set -e

echo "========================================="
echo "Floating VSCode Opener - Instalador"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}Error: Este script solo funciona en Linux${NC}"
    exit 1
fi

# Check if VSCode is installed
if ! command -v code &> /dev/null && ! command -v code-insiders &> /dev/null; then
    echo -e "${YELLOW}Advertencia: VSCode no parece estar instalado o 'code' no está en el PATH${NC}"
    echo "Puedes instalar VSCode desde: https://code.visualstudio.com/"
    echo ""
fi

echo -e "${BLUE}Paso 1: Instalando dependencias del sistema...${NC}"
echo ""

# Install system dependencies
echo "Instalando dependencias necesarias..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 xdotool

echo ""
echo -e "${BLUE}Paso 2: Instalando dependencias de Python...${NC}"
pip3 install --user PyGObject 2>/dev/null || echo "PyGObject ya instalado"

echo ""
echo -e "${BLUE}Paso 3: Configurando la aplicación...${NC}"

# Make the script executable
chmod +x floating_button.py

# Create desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/vscode-opener.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=VSCode Opener
Comment=Botón flotante para abrir carpetas en VSCode
Exec=SCRIPT_PATH
Icon=com.visualstudio.code
Terminal=false
Categories=Utility;Development;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# Replace SCRIPT_PATH with actual path
SCRIPT_PATH="$(pwd)/floating_button.py"
sed -i "s|SCRIPT_PATH|$SCRIPT_PATH|g" "$DESKTOP_FILE"

echo -e "${GREEN}Archivo desktop creado: $DESKTOP_FILE${NC}"

# Create autostart entry
AUTOSTART_FILE="$HOME/.config/autostart/vscode-opener.desktop"
mkdir -p "$HOME/.config/autostart"
cp "$DESKTOP_FILE" "$AUTOSTART_FILE"

echo -e "${GREEN}Inicio automático configurado${NC}"

echo ""
echo -e "${BLUE}Paso 4: Iniciando la aplicación...${NC}"

# Kill any existing instance
pkill -f "floating_button.py" 2>/dev/null || true
sleep 1

# Start the application in background
nohup python3 floating_button.py > /dev/null 2>&1 &

sleep 2

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Instalación completada con éxito!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}Características:${NC}"
echo "  • Botón flotante visible en pantalla"
echo "  • Detecta la carpeta activa de Nautilus"
echo "  • Click izquierdo: Abrir en VSCode"
echo "  • Click derecho: Menú de opciones"
echo "  • Arrastra el botón para moverlo"
echo ""
echo -e "${BLUE}La aplicación ya está ejecutándose!${NC}"
echo ""
echo "Para configurar: Click derecho en el botón → Configuración"
echo "Para detener: Click derecho en el botón → Salir"
echo ""
echo "La aplicación se iniciará automáticamente al iniciar sesión."
echo ""
