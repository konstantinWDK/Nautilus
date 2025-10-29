#!/bin/bash

# Script de instalación para Nautilus VSCode Widget
# Este script crea un acceso directo en el menú de aplicaciones

set -e

echo "====================================================="
echo "  Instalación de Nautilus VSCode Widget v3.3.8"
echo "====================================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Obtener la ruta del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WIDGET_PATH="$SCRIPT_DIR/nautilus-vscode-widget.py"

# Verificar que el archivo existe
if [ ! -f "$WIDGET_PATH" ]; then
    echo -e "${RED}❌ Error: No se encuentra nautilus-vscode-widget.py${NC}"
    exit 1
fi

# Verificar dependencias de Python
echo "🔍 Verificando dependencias..."
if ! python3 -c "import gi" 2>/dev/null; then
    echo -e "${RED}❌ Error: python3-gi no está instalado${NC}"
    echo "Instala las dependencias con:"
    echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    exit 1
fi

if ! python3 -c "from gi.repository import Gtk" 2>/dev/null; then
    echo -e "${RED}❌ Error: GTK3 no está disponible${NC}"
    echo "Instala las dependencias con:"
    echo "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    exit 1
fi

# Verificar dependencias adicionales
echo "🔍 Verificando dependencias adicionales..."
if ! python3 -c "import cairo" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  python3-cairo no está instalado${NC}"
    echo "Instala con: sudo apt install python3-cairo"
fi

if ! python3 -c "import json" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  python3-json no está disponible${NC}"
fi

# Verificar herramientas del sistema
echo "🔍 Verificando herramientas del sistema..."
if ! command -v xdotool &> /dev/null; then
    echo -e "${YELLOW}⚠️  xdotool no está instalado (recomendado para mejor detección)${NC}"
    echo "Instala con: sudo apt install xdotool"
fi

if ! command -v gdbus &> /dev/null; then
    echo -e "${YELLOW}⚠️  gdbus no está disponible (recomendado para Nautilus moderno)${NC}"
fi

echo -e "${GREEN}✓ Dependencias verificadas${NC}"

# Detener versiones anteriores que puedan estar ejecutándose
echo ""
echo "🔄 Deteniendo versiones anteriores..."
if pkill -f "nautilus-vscode-widget" 2>/dev/null; then
    echo -e "${GREEN}✓ Proceso anterior detenido${NC}"
    sleep 1
else
    echo "  No hay procesos anteriores en ejecución"
fi

# Verificar si hay una instalación de paquete .deb
if dpkg -l 2>/dev/null | grep -q "nautilus-vscode-widget"; then
    echo ""
    echo -e "${YELLOW}⚠️  Se detectó una instalación de paquete .deb anterior.${NC}"
    echo "   Para evitar conflictos, se recomienda desinstalarlo primero:"
    echo "   sudo apt remove nautilus-vscode-widget"
    echo ""
    read -p "¿Deseas continuar de todas formas? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Instalación cancelada."
        exit 1
    fi
fi

# Crear directorio de aplicaciones si no existe
echo ""
echo "📁 Creando estructura de directorios..."
APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"
echo -e "${GREEN}✓ $APPLICATIONS_DIR${NC}"

# Crear directorio de configuración
CONFIG_DIR="$HOME/.config/nautilus-vscode-widget"
mkdir -p "$CONFIG_DIR"
echo -e "${GREEN}✓ $CONFIG_DIR${NC}"

# Crear directorio de logs
LOG_DIR="$HOME/.local/share/nautilus-vscode-widget"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ $LOG_DIR${NC}"

# Crear archivo .desktop
echo ""
echo "🔧 Creando archivo .desktop..."
DESKTOP_FILE="$APPLICATIONS_DIR/nautilus-vscode-widget.desktop"

cat > "$DESKTOP_FILE" << INNEREOF
[Desktop Entry]
Type=Application
Name=Nautilus VSCode Widget
Comment=Widget para abrir carpetas de Nautilus en VSCode
Exec=python3 "$WIDGET_PATH"
Icon=com.visualstudio.code
Terminal=false
Categories=Utility;Development;
StartupNotify=false
Keywords=vscode;nautilus;files;folder;development;
INNEREOF

# Hacer los archivos ejecutables
chmod +x "$DESKTOP_FILE"
chmod +x "$WIDGET_PATH"

echo -e "${GREEN}✓ Archivo .desktop creado${NC}"

# Actualizar base de datos de aplicaciones
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✅ Instalación completada exitosamente!${NC}"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'Nautilus VSCode Widget' en el menú de aplicaciones"
echo "  2. Ejecutar directamente: python3 $WIDGET_PATH"
echo "  3. Configurar inicio automático desde las opciones del widget"
echo ""
echo "🎨 Características:"
echo "  • Widget ultra-compacto de 36x36 píxeles"
echo "  • Círculo oscuro elegante (#2C2C2C)"
echo "  • Solo el icono de VSCode, sin etiquetas"
echo "  • Se oculta cuando no estás en Nautilus (o siempre visible si lo prefieres)"
echo "  • Sistema de carpetas favoritas con acceso rápido"
echo "  • Click derecho para configuración"
echo "  • Opción de inicio automático en el sistema"
echo ""
echo "💡 Tip: Arrastra el widget a tu esquina favorita"
echo ""
echo "📂 Archivos instalados:"
echo "  • Desktop entry: $DESKTOP_FILE"
echo "  • Configuración: $CONFIG_DIR"
echo "  • Logs: $LOG_DIR"
echo ""
echo "Para desinstalar, ejecuta: ./uninstall.sh"
echo ""
echo "====================================================="
