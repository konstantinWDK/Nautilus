#!/bin/bash

# Quick run script for Nautilus VSCode Widget

cd "$(dirname "$0")"

# Kill any existing instance
pkill -f "nautilus-vscode-widget.py" 2>/dev/null || true

echo "Iniciando Nautilus VSCode Widget..."

# Run the application in background with nohup to prevent it from dying
# Redirect to log file for debugging
nohup python3 nautilus-vscode-widget.py > nautilus-vscode-widget.log 2>&1 &

# Get the process ID
PID=$!

echo "Nautilus VSCode Widget iniciado (PID: $PID)"
echo "Para detenerlo: pkill -f nautilus-vscode-widget.py"
echo "Para ver si está ejecutándose: pgrep -f nautilus-vscode-widget.py"

# Wait a moment to see if it starts successfully
sleep 2

if ps -p $PID > /dev/null; then
    echo "✅ Aplicación iniciada correctamente"
else
    echo "❌ Error al iniciar la aplicación"
    echo "Revisa el log: cat nautilus-vscode-widget.log"
    exit 1
fi
