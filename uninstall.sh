#!/bin/bash

# Uninstallation script for Nautilus VSCode Widget

set -e

echo "========================================="
echo "Nautilus VSCode Widget - Desinstalador"
echo "========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop the application
echo "Deteniendo la aplicación..."
pkill -f "nautilus-vscode-widget.py" 2>/dev/null && echo -e "${GREEN}Aplicación detenida${NC}" || echo "La aplicación no estaba en ejecución"

# Remove desktop entries (current and old versions)
echo ""
echo "Eliminando archivos .desktop..."
DESKTOP_FILE="$HOME/.local/share/applications/nautilus-vscode-widget.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo -e "${GREEN}✓ nautilus-vscode-widget.desktop eliminado${NC}"
fi

# Remove old desktop files
OLD_DESKTOP="$HOME/.local/share/applications/nautilus-vscode-opener.desktop"
if [ -f "$OLD_DESKTOP" ]; then
    rm "$OLD_DESKTOP"
    echo -e "${GREEN}✓ nautilus-vscode-opener.desktop (antiguo) eliminado${NC}"
fi

# Remove autostart entries (current and old versions)
echo ""
echo "Eliminando archivos de autostart..."
AUTOSTART_FILE="$HOME/.config/autostart/nautilus-vscode-widget.desktop"
if [ -f "$AUTOSTART_FILE" ]; then
    rm "$AUTOSTART_FILE"
    echo -e "${GREEN}✓ Autostart eliminado${NC}"
fi

# Remove old autostart files
OLD_AUTOSTART="$HOME/.config/autostart/nautilus-vscode-opener.desktop"
if [ -f "$OLD_AUTOSTART" ]; then
    rm "$OLD_AUTOSTART"
    echo -e "${GREEN}✓ Autostart antiguo eliminado${NC}"
fi

# Remove config directory
CONFIG_DIR="$HOME/.config/nautilus-vscode-widget"
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
