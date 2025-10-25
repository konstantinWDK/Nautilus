#!/bin/bash

# Script de instalación para Nautilus VSCode Widget
# Este script crea un acceso directo en el menú de aplicaciones

echo "====================================================="
echo "  Instalación de Nautilus VSCode Widget v2.0"
echo "====================================================="
echo ""

# Obtener la ruta del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FLOATING_BUTTON_PATH="$SCRIPT_DIR/nautilus-vscode-widget.py"

# Verificar que el archivo existe
if [ ! -f "$FLOATING_BUTTON_PATH" ]; then
    echo "❌ Error: No se encuentra nautilus-vscode-widget.py"
    exit 1
fi

# Crear directorio de aplicaciones si no existe
APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"

# Crear archivo .desktop
DESKTOP_FILE="$APPLICATIONS_DIR/nautilus-vscode-widget.desktop"

cat > "$DESKTOP_FILE" << INNEREOF
[Desktop Entry]
Type=Application
Name=Nautilus VSCode Widget
Comment=Botón flotante ultra-compacto para abrir carpetas en VSCode
Exec=python3 "$FLOATING_BUTTON_PATH"
Icon=com.visualstudio.code
Terminal=false
Categories=Utility;Development;
StartupNotify=false
Keywords=vscode;nautilus;files;folder;development;
INNEREOF

# Hacer el archivo ejecutable
chmod +x "$DESKTOP_FILE"
chmod +x "$FLOATING_BUTTON_PATH"

echo "✅ Instalación completada!"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'Nautilus VSCode Widget' en el menú de aplicaciones"
echo "  2. Ejecutar: python3 $FLOATING_BUTTON_PATH"
echo "  3. Configurar inicio automático desde las opciones del botón"
echo ""
echo "🎨 Características del nuevo diseño:"
echo "  • Botón ultra-compacto de 36x36 píxeles"
echo "  • Círculo oscuro elegante (#2C2C2C)"
echo "  • Solo el icono de VSCode, sin etiquetas"
echo "  • Se oculta suavemente cuando no estás en Nautilus"
echo "  • Aparece suavemente cuando seleccionas una ventana de Nautilus"
echo "  • Click derecho para configuración"
echo "  • Opción de inicio automático en el sistema"
echo ""
echo "💡 Tip: Arrastra el botón a tu esquina favorita"
echo ""
echo "====================================================="
