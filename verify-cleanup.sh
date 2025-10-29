#!/bin/bash
# Script para verificar que no quedan restos del Nautilus VSCode Widget
# Después de ejecutar cleanup-installation.sh

echo "====================================================="
echo "  VERIFICACIÓN DE LIMPIEZA - Nautilus VSCode Widget"
echo "====================================================="
echo ""

# Colores para mejor visualización
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔍 VERIFICANDO PROCESOS EN EJECUCIÓN...${NC}"
PROCESSES=$(pgrep -f "nautilus-vscode" 2>/dev/null || true)
if [ -n "$PROCESSES" ]; then
    echo -e "${RED}❌ PROCESOS RESIDUALES ENCONTRADOS:${NC}"
    echo "$PROCESSES"
else
    echo -e "${GREEN}✓ No hay procesos en ejecución${NC}"
fi

echo ""
echo -e "${CYAN}🔍 VERIFICANDO PAQUETE .deb...${NC}"
if dpkg -l 2>/dev/null | grep -q "nautilus-vscode-widget"; then
    echo -e "${RED}❌ PAQUETE .deb AÚN INSTALADO${NC}"
    dpkg -l | grep "nautilus-vscode-widget"
else
    echo -e "${GREEN}✓ Paquete .deb no está instalado${NC}"
fi

echo ""
echo -e "${CYAN}🔍 VERIFICANDO ARCHIVOS DEL SISTEMA...${NC}"
SYSTEM_FILES=(
    "/usr/bin/nautilus-vscode-widget"
    "/usr/share/nautilus-vscode-widget"
    "/usr/share/applications/nautilus-vscode-widget.desktop"
    "/usr/share/doc/nautilus-vscode-widget"
    "/usr/local/bin/nautilus-vscode-widget"
    "/opt/nautilus-vscode-widget"
    "/usr/bin/nautilus-vscode-opener"
    "/usr/share/nautilus-vscode-opener"
    "/usr/share/applications/nautilus-vscode-opener.desktop"
    "/usr/local/bin/nautilus-vscode-opener"
    "/opt/nautilus-vscode-opener"
)

SYSTEM_REMAINING=0
for file in "${SYSTEM_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${RED}❌ ARCHIVO DEL SISTEMA: $file${NC}"
        SYSTEM_REMAINING=$((SYSTEM_REMAINING + 1))
    fi
done

if [ $SYSTEM_REMAINING -eq 0 ]; then
    echo -e "${GREEN}✓ No hay archivos del sistema residuales${NC}"
fi

echo ""
echo -e "${CYAN}🔍 VERIFICANDO ARCHIVOS DE USUARIO...${NC}"
USER_FILES=(
    "$HOME/.config/nautilus-vscode-widget"
    "$HOME/.local/share/nautilus-vscode-widget"
    "$HOME/.local/share/applications/nautilus-vscode-widget.desktop"
    "$HOME/.config/autostart/nautilus-vscode-widget.desktop"
    "$HOME/.cache/nautilus-vscode-widget"
    "$HOME/Desktop/nautilus-vscode-widget.desktop"
    "$HOME/Escritorio/nautilus-vscode-widget.desktop"
    "$HOME/.config/nautilus-vscode-opener"
    "$HOME/.local/share/nautilus-vscode-opener"
    "$HOME/.local/share/applications/nautilus-vscode-opener.desktop"
    "$HOME/.config/autostart/nautilus-vscode-opener.desktop"
    "$HOME/Desktop/nautilus-vscode-opener.desktop"
    "$HOME/Escritorio/nautilus-vscode-opener.desktop"
)

USER_REMAINING=0
for file in "${USER_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${RED}❌ ARCHIVO DE USUARIO: $file${NC}"
        USER_REMAINING=$((USER_REMAINING + 1))
    fi
done

if [ $USER_REMAINING -eq 0 ]; then
    echo -e "${GREEN}✓ No hay archivos de usuario residuales${NC}"
fi

echo ""
echo -e "${CYAN}🔍 VERIFICANDO LOGS Y ARCHIVOS TEMPORALES...${NC}"
TEMP_FILES=(
    "$HOME/.local/share/nautilus-vscode-widget/widget.log"
    "/var/log/nautilus-vscode-widget"
    "/tmp/nautilus-vscode-widget*"
    "/tmp/nautilus-vscode-opener*"
    "/tmp/vscode-widget*"
    "$HOME/.cache/nautilus-vscode-widget"
    "$HOME/.cache/nautilus-vscode-opener"
)

TEMP_REMAINING=0
for pattern in "${TEMP_FILES[@]}"; do
    for file in $pattern; do
        if [ -e "$file" ]; then
            echo -e "${RED}❌ ARCHIVO TEMPORAL: $file${NC}"
            TEMP_REMAINING=$((TEMP_REMAINING + 1))
        fi
    done
done

if [ $TEMP_REMAINING -eq 0 ]; then
    echo -e "${GREEN}✓ No hay archivos temporales residuales${NC}"
fi

echo ""
echo -e "${CYAN}🔍 VERIFICANDO ARCHIVOS DE DPKG...${NC}"
DPKG_FILES=(
    "/var/lib/dpkg/info/nautilus-vscode-widget.*"
    "/var/lib/dpkg/triggers/nautilus-vscode-widget"
    "/var/cache/apt/archives/nautilus-vscode-widget*"
)

DPKG_REMAINING=0
for pattern in "${DPKG_FILES[@]}"; do
    for file in $pattern; do
        if [ -e "$file" ]; then
            echo -e "${RED}❌ ARCHIVO DPKG: $file${NC}"
            DPKG_REMAINING=$((DPKG_REMAINING + 1))
        fi
    done
done

if [ $DPKG_REMAINING -eq 0 ]; then
    echo -e "${GREEN}✓ No hay archivos de dpkg residuales${NC}"
fi

echo ""
echo -e "${CYAN}📊 RESUMEN DE VERIFICACIÓN${NC}"
TOTAL_REMAINING=$((SYSTEM_REMAINING + USER_REMAINING + TEMP_REMAINING + DPKG_REMAINING))

if [ -n "$PROCESSES" ]; then
    TOTAL_REMAINING=$((TOTAL_REMAINING + 1))
fi

if dpkg -l 2>/dev/null | grep -q "nautilus-vscode-widget"; then
    TOTAL_REMAINING=$((TOTAL_REMAINING + 1))
fi

if [ $TOTAL_REMAINING -eq 0 ]; then
    echo -e "${GREEN}✅ ¡SISTEMA COMPLETAMENTE LIMPIO!${NC}"
    echo -e "${GREEN}No se encontraron restos del Nautilus VSCode Widget${NC}"
else
    echo -e "${YELLOW}⚠️  SE ENCONTRARON RESTOS: $TOTAL_REMAINING${NC}"
    echo ""
    echo -e "${YELLOW}Para eliminar los restos, ejecuta:${NC}"
    echo -e "${CYAN}./cleanup-installation.sh${NC}"
    echo ""
    echo -e "${YELLOW}O ejecuta manualmente:${NC}"
    if [ -n "$PROCESSES" ]; then
        echo -e "${CYAN}pkill -9 -f 'nautilus-vscode'${NC}"
    fi
    if dpkg -l 2>/dev/null | grep -q "nautilus-vscode-widget"; then
        echo -e "${CYAN}sudo dpkg --purge nautilus-vscode-widget${NC}"
    fi
fi

echo ""
echo -e "${CYAN}=====================================================${NC}"
