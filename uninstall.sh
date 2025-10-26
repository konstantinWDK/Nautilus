#!/bin/bash

# Uninstallation script for Nautilus VSCode Widget
# Elimina todos los archivos, configuraciones y datos temporales

set -e

echo "========================================="
echo "Nautilus VSCode Widget - Desinstalador"
echo "========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Stop the application
echo "🛑 Deteniendo la aplicación..."
if pkill -f "nautilus-vscode-widget.py" 2>/dev/null; then
    echo -e "${GREEN}✓ Aplicación detenida${NC}"
    sleep 1
elif pkill -f "nautilus-vscode-widget" 2>/dev/null; then
    echo -e "${GREEN}✓ Aplicación detenida${NC}"
    sleep 1
else
    echo "  La aplicación no estaba en ejecución"
fi

# Remove desktop entries (current and old versions)
echo ""
echo "🗑️  Eliminando archivos .desktop..."
FILES_REMOVED=0

DESKTOP_FILE="$HOME/.local/share/applications/nautilus-vscode-widget.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo -e "${GREEN}✓ nautilus-vscode-widget.desktop eliminado${NC}"
    FILES_REMOVED=$((FILES_REMOVED + 1))
fi

# Remove old desktop files
OLD_DESKTOP="$HOME/.local/share/applications/nautilus-vscode-opener.desktop"
if [ -f "$OLD_DESKTOP" ]; then
    rm "$OLD_DESKTOP"
    echo -e "${GREEN}✓ nautilus-vscode-opener.desktop (antiguo) eliminado${NC}"
    FILES_REMOVED=$((FILES_REMOVED + 1))
fi

if [ $FILES_REMOVED -eq 0 ]; then
    echo "  No se encontraron archivos .desktop"
fi

# Remove autostart entries (current and old versions)
echo ""
echo "🗑️  Eliminando archivos de autostart..."
FILES_REMOVED=0

AUTOSTART_FILE="$HOME/.config/autostart/nautilus-vscode-widget.desktop"
if [ -f "$AUTOSTART_FILE" ]; then
    rm "$AUTOSTART_FILE"
    echo -e "${GREEN}✓ Autostart eliminado${NC}"
    FILES_REMOVED=$((FILES_REMOVED + 1))
fi

# Remove old autostart files
OLD_AUTOSTART="$HOME/.config/autostart/nautilus-vscode-opener.desktop"
if [ -f "$OLD_AUTOSTART" ]; then
    rm "$OLD_AUTOSTART"
    echo -e "${GREEN}✓ Autostart antiguo eliminado${NC}"
    FILES_REMOVED=$((FILES_REMOVED + 1))
fi

if [ $FILES_REMOVED -eq 0 ]; then
    echo "  No se encontraron archivos de autostart"
fi

# Remove config directory
echo ""
echo "🗑️  Eliminando configuración..."
CONFIG_DIR="$HOME/.config/nautilus-vscode-widget"
if [ -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}📁 Se encontró el directorio de configuración:${NC}"
    echo "   $CONFIG_DIR"
    if [ -f "$CONFIG_DIR/config.json" ]; then
        echo -e "${BLUE}   Contiene: config.json (posición del widget, carpetas favoritas, etc.)${NC}"
    fi
    echo ""
    echo -e "${YELLOW}¿Deseas eliminar la configuración? (s/n)${NC}"
    read -r -n 1 response
    echo
    if [[ "$response" =~ ^[Ss]$ ]]; then
        rm -rf "$CONFIG_DIR"
        echo -e "${GREEN}✓ Configuración eliminada${NC}"
    else
        echo -e "${BLUE}✓ Configuración conservada${NC}"
    fi
else
    echo "  No se encontró directorio de configuración"
fi

# Remove log directory
echo ""
echo "🗑️  Eliminando archivos de log y temporales..."
LOG_DIR="$HOME/.local/share/nautilus-vscode-widget"
if [ -d "$LOG_DIR" ]; then
    echo -e "${YELLOW}📁 Se encontró el directorio de logs:${NC}"
    echo "   $LOG_DIR"
    if [ -f "$LOG_DIR/widget.log" ]; then
        LOG_SIZE=$(du -h "$LOG_DIR/widget.log" 2>/dev/null | cut -f1)
        echo -e "${BLUE}   Contiene: widget.log ($LOG_SIZE)${NC}"
    fi
    echo ""
    echo -e "${YELLOW}¿Deseas eliminar los logs y archivos temporales? (s/n)${NC}"
    read -r -n 1 response
    echo
    if [[ "$response" =~ ^[Ss]$ ]]; then
        rm -rf "$LOG_DIR"
        echo -e "${GREEN}✓ Logs y temporales eliminados${NC}"
    else
        echo -e "${BLUE}✓ Logs conservados${NC}"
    fi
else
    echo "  No se encontró directorio de logs"
fi

# Remove possible cached icon
echo ""
echo "🗑️  Verificando ícono cacheado..."
ICON_FILE="$HOME/.local/share/icons/vscode.png"
if [ -f "$ICON_FILE" ]; then
    echo -e "${YELLOW}Se encontró ícono cacheado: $ICON_FILE${NC}"
    echo -e "${YELLOW}¿Deseas eliminarlo? (s/n)${NC}"
    read -r -n 1 response
    echo
    if [[ "$response" =~ ^[Ss]$ ]]; then
        rm "$ICON_FILE"
        echo -e "${GREEN}✓ Ícono eliminado${NC}"
    else
        echo -e "${BLUE}✓ Ícono conservado${NC}"
    fi
else
    echo "  No se encontró ícono cacheado"
fi

# Update desktop database
echo ""
echo "🔄 Actualizando base de datos de aplicaciones..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo -e "${GREEN}✓ Base de datos actualizada${NC}"
fi

# Check for .deb installation
echo ""
if dpkg -l 2>/dev/null | grep -q "nautilus-vscode-widget"; then
    echo -e "${YELLOW}⚠️  Nota: También tienes instalada la versión .deb del paquete${NC}"
    echo "   Para desinstalarla completamente, ejecuta:"
    echo "   sudo apt remove nautilus-vscode-widget"
    echo ""
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ Desinstalación completada${NC}"
echo "========================================="
echo ""
echo "📂 Archivos eliminados:"
echo "  • Desktop entries: ~/.local/share/applications/"
echo "  • Autostart: ~/.config/autostart/"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "  • Configuración: ~/.config/nautilus-vscode-widget/"
fi
if [ ! -d "$LOG_DIR" ]; then
    echo "  • Logs: ~/.local/share/nautilus-vscode-widget/"
fi
echo ""
echo "📁 Los archivos del código fuente siguen en:"
echo "   $(pwd)"
echo ""
echo "   Si deseas eliminarlos también, ejecuta:"
echo "   cd .. && rm -rf $(basename $(pwd))"
echo ""
