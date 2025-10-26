#!/bin/bash
# Script para crear paquete .deb de Nautilus VSCode Widget

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Nautilus VSCode Widget - Generador de Paquete .deb       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
DEBIAN_DIR="$SCRIPT_DIR/debian"

# Verificar que existe el programa
if [ ! -f "$PROJECT_DIR/nautilus-vscode-widget.py" ]; then
    echo -e "${RED}Error: No se encuentra nautilus-vscode-widget.py${NC}"
    exit 1
fi

# Limpiar builds anteriores
echo -e "${YELLOW}Limpiando builds anteriores...${NC}"
rm -rf "$DEBIAN_DIR/usr" 2>/dev/null || true
rm -f "$SCRIPT_DIR"/*.deb 2>/dev/null || true
rm -f "$PROJECT_DIR"/dist/*.deb 2>/dev/null || true

# Verificar si hay una versión anterior instalada y forzar su eliminación si es necesario
if dpkg -l | grep -q "nautilus-vscode-widget"; then
    echo -e "${YELLOW}Se detectó una versión anterior instalada. Forzando actualización...${NC}"
    # Crear un script temporal para limpiar la instalación anterior
    cat > /tmp/cleanup-nautilus-widget.sh << 'EOF'
#!/bin/bash
# Script para limpiar instalación anterior de nautilus-vscode-widget

set -e

echo "Limpiando instalación anterior de Nautilus VSCode Widget..."

# Detener el programa si está corriendo
pkill -f "nautilus-vscode-widget" 2>/dev/null || true
pkill -f "nautilus-vscode-widget.py" 2>/dev/null || true

# Limpiar archivos de dpkg si el paquete está en estado inconsistente
if dpkg -l | grep -q "nautilus-vscode-widget"; then
    # Mover archivos de info a /tmp para limpiar estado
    mv /var/lib/dpkg/info/nautilus-vscode-widget.* /tmp/ 2>/dev/null || true
    # Forzar eliminación del paquete
    dpkg --remove --force-remove-reinstreq nautilus-vscode-widget 2>/dev/null || true
fi

# Eliminar archivos manualmente por si acaso
rm -f /usr/bin/nautilus-vscode-widget 2>/dev/null || true
rm -rf /usr/share/nautilus-vscode-widget 2>/dev/null || true
rm -f /usr/share/applications/nautilus-vscode-widget.desktop 2>/dev/null || true
rm -rf /usr/share/doc/nautilus-vscode-widget 2>/dev/null || true

echo "Limpieza completada. Listo para nueva instalación."
EOF

    chmod +x /tmp/cleanup-nautilus-widget.sh
    echo -e "${YELLOW}Ejecuta el siguiente comando para limpiar la instalación anterior:${NC}"
    echo -e "  ${CYAN}sudo /tmp/cleanup-nautilus-widget.sh${NC}"
    echo ""
fi

# Crear estructura de directorios
echo -e "${CYAN}Creando estructura de directorios...${NC}"
mkdir -p "$DEBIAN_DIR/usr/bin"
mkdir -p "$DEBIAN_DIR/usr/share/nautilus-vscode-widget"
mkdir -p "$DEBIAN_DIR/usr/share/applications"
mkdir -p "$DEBIAN_DIR/usr/share/doc/nautilus-vscode-widget"

# Copiar el programa
echo -e "${CYAN}Copiando archivos del programa...${NC}"
cp "$PROJECT_DIR/nautilus-vscode-widget.py" "$DEBIAN_DIR/usr/share/nautilus-vscode-widget/"
chmod +x "$DEBIAN_DIR/usr/share/nautilus-vscode-widget/nautilus-vscode-widget.py"

# Crear script lanzador en /usr/bin
cat > "$DEBIAN_DIR/usr/bin/nautilus-vscode-widget" << 'EOF'
#!/bin/bash
# Lanzador de Nautilus VSCode Widget
cd /usr/share/nautilus-vscode-widget
python3 /usr/share/nautilus-vscode-widget/nautilus-vscode-widget.py &
EOF

chmod +x "$DEBIAN_DIR/usr/bin/nautilus-vscode-widget"

# Crear archivo .desktop
cat > "$DEBIAN_DIR/usr/share/applications/nautilus-vscode-widget.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Nautilus VSCode Widget
Comment=Open Nautilus folders in VSCode
Exec=nautilus-vscode-widget
Icon=com.visualstudio.code
Terminal=false
Categories=Utility;Development;GNOME;GTK;
Keywords=nautilus;vscode;files;folder;
StartupNotify=false
EOF

# Crear copyright
cat > "$DEBIAN_DIR/usr/share/doc/nautilus-vscode-widget/copyright" << 'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: nautilus-vscode-widget
Source: https://github.com/konstantinWDK/nautilus-vscode-widget

Files: *
Copyright: 2025 Tu Nombre
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
EOF

# Leer versión del archivo control
VERSION=$(grep "^Version:" "$DEBIAN_DIR/DEBIAN/control" | cut -d' ' -f2)
PACKAGE_NAME="nautilus-vscode-widget_${VERSION}_all.deb"

# Construir el paquete
echo -e "${CYAN}Construyendo paquete .deb...${NC}"
mkdir -p "$PROJECT_DIR/dist"
cd "$PROJECT_DIR"
dpkg-deb --build --root-owner-group linux/debian dist/"$PACKAGE_NAME"

# Verificar el paquete
if [ -f "dist/$PACKAGE_NAME" ]; then
    SIZE=$(du -h "dist/$PACKAGE_NAME" | cut -f1)

    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         ¡Paquete .deb Creado Exitosamente!                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Paquete:${NC} ${GREEN}$PACKAGE_NAME${NC}"
    echo -e "${CYAN}Tamaño:${NC} ${GREEN}$SIZE${NC}"
    echo -e "${CYAN}Ubicación:${NC} ${GREEN}./dist/$PACKAGE_NAME${NC}"
    echo ""

    echo -e "${BLUE}Información del paquete:${NC}"
    dpkg-deb --info "dist/$PACKAGE_NAME"

    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  PARA INSTALAR:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}Opción 1: Instalación automática con dependencias${NC}"
    echo -e "  ${GREEN}sudo apt install ./dist/$PACKAGE_NAME${NC}"
    echo ""
    echo -e "${CYAN}Opción 2: Instalación manual (requiere dependencias previas)${NC}"
    echo -e "  ${CYAN}sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 xdotool wmctrl${NC}"
    echo -e "  ${CYAN}sudo dpkg -i dist/$PACKAGE_NAME${NC}"
    echo ""
    echo -e "  ${BLUE}O con doble clic en el archivo .deb${NC}"
    echo ""
    echo -e "${YELLOW}  PARA DESINSTALAR:${NC}"
    echo ""
    echo -e "  ${CYAN}sudo apt remove nautilus-vscode-widget${NC}"
    echo ""
    echo -e "${GREEN}¡Listo para distribuir!${NC}"
    echo ""
    echo -e "${CYAN}✨ El paquete .deb instalará las dependencias automáticamente${NC}"
    echo ""
else
    echo -e "${RED}Error: No se pudo crear el paquete .deb${NC}"
    exit 1
fi
