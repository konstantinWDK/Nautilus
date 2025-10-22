#!/bin/bash

# Uninstallation script for Floating VSCode Opener

set -e

echo "========================================="
echo "Floating VSCode Opener - Desinstalador"
echo "========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop the application
echo "Deteniendo la aplicación..."
pkill -f "floating_button.py" 2>/dev/null && echo -e "${GREEN}Aplicación detenida${NC}" || echo "La aplicación no estaba en ejecución"

# Remove desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/vscode-opener.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo -e "${GREEN}Archivo desktop eliminado${NC}"
fi

# Remove autostart entry
AUTOSTART_FILE="$HOME/.config/autostart/vscode-opener.desktop"
if [ -f "$AUTOSTART_FILE" ]; then
    rm "$AUTOSTART_FILE"
    echo -e "${GREEN}Inicio automático deshabilitado${NC}"
fi

# Remove config directory
CONFIG_DIR="$HOME/.config/nautilus-vscode-opener"
if [ -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}¿Deseas eliminar la configuración? (s/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        rm -rf "$CONFIG_DIR"
        echo -e "${GREEN}Configuración eliminada${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Desinstalación completada${NC}"
echo ""
echo "Los archivos del proyecto siguen en:"
echo "$(pwd)"
echo ""
