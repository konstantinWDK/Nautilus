#!/bin/bash
# Script de limpieza para Nautilus VSCode Widget
# Resuelve conflictos de instalación entre versiones

echo "====================================================="
echo "  Limpieza de Instalación - Nautilus VSCode Widget"
echo "====================================================="
echo ""

echo "🔄 Deteniendo procesos en ejecución..."
pkill -f "nautilus-vscode-widget" 2>/dev/null || true
pkill -f "nautilus-vscode-widget.py" 2>/dev/null || true

# Esperar para asegurar que los procesos se detengan
sleep 2

echo "🗑️  Limpiando instalaciones anteriores..."

# Limpiar instalación de paquete .deb si existe
if dpkg -l | grep -q "nautilus-vscode-widget"; then
    echo "📦 Eliminando paquete .deb instalado..."
    sudo dpkg --remove --force-remove-reinstreq nautilus-vscode-widget 2>/dev/null || true
    sudo apt remove --purge nautilus-vscode-widget 2>/dev/null || true
fi

# Limpiar archivos de dpkg si hay estado inconsistente
echo "🧹 Limpiando estado de dpkg..."
sudo mv /var/lib/dpkg/info/nautilus-vscode-widget.* /tmp/ 2>/dev/null || true

# Limpiar archivos manualmente
echo "📁 Eliminando archivos de instalación..."
sudo rm -f /usr/bin/nautilus-vscode-widget 2>/dev/null || true
sudo rm -rf /usr/share/nautilus-vscode-widget 2>/dev/null || true
sudo rm -f /usr/share/applications/nautilus-vscode-widget.desktop 2>/dev/null || true
sudo rm -rf /usr/share/doc/nautilus-vscode-widget 2>/dev/null || true

# Limpiar instalación local
echo "🏠 Limpiando instalación local..."
rm -f "$HOME/.local/share/applications/nautilus-vscode-widget.desktop" 2>/dev/null || true

# Limpiar autostart
echo "🚀 Limpiando inicio automático..."
rm -f "$HOME/.config/autostart/nautilus-vscode-widget.desktop" 2>/dev/null || true

# Limpiar configuración (opcional - comentado para preservar configuraciones)
# echo "⚙️  Limpiando configuración..."
# rm -rf "$HOME/.config/nautilus-vscode-widget" 2>/dev/null || true

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "Ahora puedes:"
echo "  1. Instalar desde el repositorio: git pull"
echo "  2. Usar install.sh para instalación local"
echo "  3. Usar linux/build-deb.sh para crear paquete .deb"
echo ""
echo "💡 Recomendación:"
echo "   Para evitar conflictos, usa solo un método de instalación:"
echo "   - O instalación local (install.sh)"
echo "   - O paquete .deb (build-deb.sh)"
echo ""
echo "====================================================="
