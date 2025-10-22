#!/bin/bash

# Quick run script for Floating VSCode Opener

cd "$(dirname "$0")"

# Kill any existing instance
pkill -f "floating_button.py" 2>/dev/null || true

echo "Iniciando VSCode Opener..."

# Run the application in background with nohup to prevent it from dying
# Redirect to log file for debugging
nohup python3 floating_button.py > floating_button.log 2>&1 &

# Get the process ID
PID=$!

echo "VSCode Opener iniciado (PID: $PID)"
echo "Para detenerlo: pkill -f floating_button.py"
echo "Para ver si está ejecutándose: pgrep -f floating_button.py"

# Wait a moment to see if it starts successfully
sleep 2

if ps -p $PID > /dev/null; then
    echo "✅ Aplicación iniciada correctamente"
else
    echo "❌ Error al iniciar la aplicación"
    exit 1
fi
