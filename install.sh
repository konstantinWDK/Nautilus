#!/bin/bash

# Script de instalación para Nautilus VSCode Widget
# Este script crea un acceso directo en el menú de aplicaciones

echo "====================================================="
echo "  Instalación de Nautilus VSCode Widget v3.1"
echo "====================================================="
echo ""

# Obtener la ruta del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WIDGET_PATH="$SCRIPT_DIR/nautilus-vscode-widget.py"

# Verificar que el archivo existe
if [ ! -f "$WIDGET_PATH" ]; then
    echo "❌ Error: No se encuentra nautilus-vscode-widget.py"
    exit 1
fi

# Detener versiones anteriores que puedan estar ejecutándose
echo "🔄 Deteniendo versiones anteriores..."
pkill -f "nautilus-vscode-widget" 2>/dev/null || true
pkill -f "nautilus-vscode-widget.py" 2>/dev/null || true

# Esperar un momento para asegurar que los procesos se detengan
sleep 1

# Verificar si hay una instalación de paquete .deb y limpiarla si es necesario
if dpkg -l | grep -q "nautilus-vscode-widget"; then
    echo "⚠️  Se detectó una instalación de paquete .deb anterior."
    echo "   Para evitar conflictos, se recomienda:"
    echo "   sudo apt remove nautilus-vscode-widget"
    echo ""
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
Comment=Widget para abrir carpetas de Nautilus en VSCode
Exec=python3 "$WIDGET_PATH"
Icon=com.visualstudio.code
Terminal=false
Categories=Utility;Development;
StartupNotify=false
Keywords=vscode;nautilus;files;folder;development;
INNEREOF

# Hacer el archivo ejecutable
chmod +x "$DESKTOP_FILE"
chmod +x "$WIDGET_PATH"

echo "✅ Instalación completada!"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'Nautilus VSCode Widget' en el menú de aplicaciones"
echo "  2. Ejecutar: python3 $WIDGET_PATH"
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
echo "====================================================="
