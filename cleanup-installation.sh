#!/bin/bash
# Script de limpieza completa para Nautilus VSCode Widget
# Elimina absolutamente todo lo instalado del sistema

echo "====================================================="
echo "  LIMPIEZA COMPLETA - Nautilus VSCode Widget"
echo "====================================================="
echo ""

# Colores para mejor visualización
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 Deteniendo procesos en ejecución...${NC}"
echo "Deteniendo todos los procesos del widget..."
pkill -f "nautilus-vscode-widget" 2>/dev/null || true
pkill -f "nautilus-vscode-widget.py" 2>/dev/null || true
pkill -f "python3.*nautilus-vscode-widget" 2>/dev/null || true

# Esperar para asegurar que los procesos se detengan
sleep 2

# Forzar cierre si es necesario
pkill -9 -f "nautilus-vscode-widget" 2>/dev/null || true
pkill -9 -f "nautilus-vscode-widget.py" 2>/dev/null || true

echo ""
echo -e "${CYAN}📦 LIMPIANDO INSTALACIÓN DE PAQUETE .deb...${NC}"

# Verificar si el paquete está instalado
if dpkg -l | grep -q "nautilus-vscode-widget" 2>/dev/null; then
    echo -e "${YELLOW}Eliminando paquete .deb instalado...${NC}"
    sudo dpkg --remove --force-all nautilus-vscode-widget 2>/dev/null || true
    sudo dpkg --purge --force-all nautilus-vscode-widget 2>/dev/null || true
    sudo apt remove --purge nautilus-vscode-widget 2>/dev/null || true
    sudo apt autoremove 2>/dev/null || true
else
    echo -e "${GREEN}No se encontró paquete .deb instalado${NC}"
fi

echo ""
echo -e "${CYAN}🧹 LIMPIANDO ARCHIVOS DEL SISTEMA...${NC}"

# Archivos del sistema que deben eliminarse
SYSTEM_FILES=(
    "/usr/bin/nautilus-vscode-widget"
    "/usr/share/nautilus-vscode-widget"
    "/usr/share/applications/nautilus-vscode-widget.desktop"
    "/usr/share/doc/nautilus-vscode-widget"
    "/usr/local/bin/nautilus-vscode-widget"
    "/opt/nautilus-vscode-widget"
)

for file in "${SYSTEM_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Eliminando: $file${NC}"
        sudo rm -rf "$file" 2>/dev/null || true
    else
        echo -e "${GREEN}No existe: $file${NC}"
    fi
done

echo ""
echo -e "${CYAN}🏠 LIMPIANDO ARCHIVOS DE USUARIO...${NC}"

# Archivos de usuario que deben eliminarse
USER_FILES=(
    "$HOME/.config/nautilus-vscode-widget"
    "$HOME/.local/share/nautilus-vscode-widget"
    "$HOME/.local/share/applications/nautilus-vscode-widget.desktop"
    "$HOME/.config/autostart/nautilus-vscode-widget.desktop"
    "$HOME/.cache/nautilus-vscode-widget"
    "$HOME/Desktop/nautilus-vscode-widget.desktop"
    "$HOME/Escritorio/nautilus-vscode-widget.desktop"
)

for file in "${USER_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Eliminando: $file${NC}"
        rm -rf "$file" 2>/dev/null || true
    else
        echo -e "${GREEN}No existe: $file${NC}"
    fi
done

echo ""
echo -e "${CYAN}🗄️  LIMPIANDO LOGS Y CACHÉ...${NC}"

# Logs y caché
LOG_FILES=(
    "$HOME/.local/share/nautilus-vscode-widget/widget.log"
    "/var/log/nautilus-vscode-widget"
    "/tmp/nautilus-vscode-widget*"
    "/tmp/nautilus-vscode-opener*"
    "/tmp/vscode-widget*"
    "$HOME/.cache/nautilus-vscode-widget"
    "$HOME/.cache/nautilus-vscode-opener"
)

for file in "${LOG_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Eliminando: $file${NC}"
        rm -rf "$file" 2>/dev/null || true
    fi
done

# Limpiar archivos temporales específicos del sistema
echo ""
echo -e "${CYAN}🧹 LIMPIANDO ARCHIVOS TEMPORALES ESPECÍFICOS...${NC}"
TEMP_FILES=(
    "/tmp/nautilus-vscode-widget*.log"
    "/tmp/nautilus-vscode-widget*.pid"
    "/tmp/nautilus-vscode-opener*.log"
    "/tmp/nautilus-vscode-opener*.pid"
    "/tmp/vscode-widget*.log"
    "/tmp/vscode-widget*.pid"
)

for pattern in "${TEMP_FILES[@]}"; do
    for file in $pattern; do
        if [ -e "$file" ]; then
            echo -e "${YELLOW}Eliminando: $file${NC}"
            rm -f "$file" 2>/dev/null || true
        fi
    done
done

# Verificar y limpiar archivos de versiones antiguas
echo ""
echo -e "${CYAN}🔍 BUSCANDO ARCHIVOS DE VERSIONES ANTIGUAS...${NC}"
OLD_FILES=(
    "$HOME/.config/nautilus-vscode-opener"
    "$HOME/.local/share/nautilus-vscode-opener"
    "$HOME/.local/share/applications/nautilus-vscode-opener.desktop"
    "$HOME/.config/autostart/nautilus-vscode-opener.desktop"
    "$HOME/Desktop/nautilus-vscode-opener.desktop"
    "$HOME/Escritorio/nautilus-vscode-opener.desktop"
    "/usr/bin/nautilus-vscode-opener"
    "/usr/share/nautilus-vscode-opener"
    "/usr/share/applications/nautilus-vscode-opener.desktop"
    "/usr/local/bin/nautilus-vscode-opener"
    "/opt/nautilus-vscode-opener"
)

for file in "${OLD_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${YELLOW}Eliminando archivo antiguo: $file${NC}"
        sudo rm -rf "$file" 2>/dev/null || true
    fi
done

# Verificar procesos residuales
echo ""
echo -e "${CYAN}🔍 VERIFICANDO PROCESOS RESIDUALES...${NC}"
RESIDUAL_PROCESSES=$(pgrep -f "nautilus-vscode" 2>/dev/null || true)
if [ -n "$RESIDUAL_PROCESSES" ]; then
    echo -e "${YELLOW}Se encontraron procesos residuales, forzando cierre...${NC}"
    pkill -9 -f "nautilus-vscode" 2>/dev/null || true
    sleep 1
else
    echo -e "${GREEN}No se encontraron procesos residuales${NC}"
fi

echo ""
echo -e "${CYAN}🔧 LIMPIANDO ESTADO DE DPKG...${NC}"

# Limpiar archivos de dpkg
DPKG_FILES=(
    "/var/lib/dpkg/info/nautilus-vscode-widget.*"
    "/var/lib/dpkg/triggers/nautilus-vscode-widget"
    "/var/cache/apt/archives/nautilus-vscode-widget*"
)

for file in "${DPKG_FILES[@]}"; do
    if ls $file 2>/dev/null; then
        echo -e "${YELLOW}Eliminando: $file${NC}"
        sudo rm -f $file 2>/dev/null || true
    fi
done

# Reparar dpkg si es necesario
echo -e "${CYAN}Reparando dpkg...${NC}"
sudo dpkg --configure -a 2>/dev/null || true

echo ""
echo -e "${CYAN}🔄 ACTUALIZANDO BASES DE DATOS DEL SISTEMA...${NC}"

# Actualizar bases de datos
sudo update-desktop-database 2>/dev/null || true
sudo update-mime-database /usr/share/mime 2>/dev/null || true

echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✅ ¡LIMPIEZA COMPLETADA EXITOSAMENTE!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo -e "${CYAN}📋 RESUMEN DE LA LIMPIEZA:${NC}"
echo -e "${CYAN}• Procesos del widget detenidos${NC}"
echo -e "${CYAN}• Paquete .deb eliminado del sistema${NC}"
echo -e "${CYAN}• Archivos del sistema eliminados${NC}"
echo -e "${CYAN}• Archivos de usuario eliminados${NC}"
echo -e "${CYAN}• Logs y caché eliminados${NC}"
echo -e "${CYAN}• Estado de dpkg limpiado${NC}"
echo -e "${CYAN}• Bases de datos del sistema actualizadas${NC}"
echo ""
echo -e "${YELLOW}💡 INFORMACIÓN IMPORTANTE:${NC}"
echo -e "${YELLOW}• Se eliminaron TODOS los archivos del widget${NC}"
echo -e "${YELLOW}• La configuración personal se perdió${NC}"
echo -e "${YELLOW}• El sistema está completamente limpio${NC}"
echo ""
echo -e "${GREEN}🎯 AHORA PUEDES:${NC}"
echo -e "${GREEN}1. Instalar una nueva versión limpia${NC}"
echo -e "${GREEN}2. Usar install.sh para instalación local${NC}"
echo -e "${GREEN}3. Usar linux/build-deb.sh para crear paquete .deb${NC}"
echo ""
echo -e "${CYAN}=====================================================${NC}"
