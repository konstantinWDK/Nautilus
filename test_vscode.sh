#!/bin/bash

# Script de prueba para verificar que VSCode se abre correctamente

echo "========================================="
echo "Test de apertura de VSCode"
echo "========================================="
echo ""

# Verificar que code existe
if ! command -v code &> /dev/null; then
    echo "❌ El comando 'code' no está disponible"
    echo ""
    echo "Verifica la instalación de VSCode:"
    echo "  which code"
    echo ""
    exit 1
fi

echo "✓ Comando 'code' encontrado en: $(which code)"
echo "✓ Versión: $(code --version | head -n 1)"
echo ""

# Crear carpeta de prueba
TEST_DIR="/tmp/test_vscode_widget"
mkdir -p "$TEST_DIR"
echo "📁 Carpeta de prueba creada: $TEST_DIR"
echo ""

# Intentar abrir VSCode
echo "🚀 Intentando abrir VSCode..."
code "$TEST_DIR" &

sleep 2

echo ""
echo "Si VSCode se abrió correctamente, el botón flotante debería funcionar."
echo ""
echo "Para probar con el botón flotante:"
echo "1. Abre Nautilus (Archivos)"
echo "2. Navega a cualquier carpeta"
echo "3. El botón flotante debería aparecer en la esquina inferior derecha"
echo "4. Haz clic en el botón"
echo ""
