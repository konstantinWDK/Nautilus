#!/bin/bash

# Script de compilación para versión portable con PyInstaller
# Genera un ejecutable autónomo que incluye todas las dependencias

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Nautilus VSCode Widget - Compilador PyInstaller Portable    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

# Verificar que PyInstaller está instalado
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller no está instalado"
    echo "📥 Instalando PyInstaller..."
    pip install pyinstaller
fi

# Limpiar builds anteriores
echo "🔄 Limpiando builds anteriores..."
rm -rf dist build *.spec 2>/dev/null || true

# Crear archivo de especificación para PyInstaller
echo "⚙️ Creando configuración de PyInstaller..."
cat > nautilus-vscode-widget.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../nautilus-vscode-widget.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gi',
        'cairo',
        'Xlib',
        'Xlib.display',
        'Xlib.protocol',
        'Xlib.X',
        'Xlib.ext',
        'Xlib.keysymdef',
        'Xlib.support',
        'Xlib.xobject',
        'gi.repository.Gtk',
        'gi.repository.Gdk',
        'gi.repository.GLib',
        'gi.repository.GdkPixbuf',
        'gi.repository.GObject',
        'gi.repository.Gio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nautilus-vscode-widget',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../icon.svg',
)
EOF

# Compilar con PyInstaller
echo "🔨 Compilando con PyInstaller..."
pyinstaller --onefile --windowed --name nautilus-vscode-widget \
    --add-data "../icon.svg:." \
    --hidden-import=gi \
    --hidden-import=cairo \
    --hidden-import=Xlib \
    --hidden-import=Xlib.display \
    --hidden-import=Xlib.protocol \
    --hidden-import=Xlib.X \
    --hidden-import=gi.repository.Gtk \
    --hidden-import=gi.repository.Gdk \
    --hidden-import=gi.repository.GLib \
    --hidden-import=gi.repository.GdkPixbuf \
    --hidden-import=gi.repository.GObject \
    --hidden-import=gi.repository.Gio \
    --icon=../icon.svg \
    ../nautilus-vscode-widget.py

# Mover el ejecutable a la carpeta dist
echo "📦 Preparando archivo final..."
mkdir -p dist
mv dist/nautilus-vscode-widget dist/nautilus-vscode-widget-portable

# Crear estructura de carpetas para modo portable
echo "📁 Creando estructura de carpetas portable..."
mkdir -p dist/conf
mkdir -p dist/logs

# Crear archivo de información en conf
cat > dist/conf/README.txt << 'EOF'
Este directorio contiene la configuración del widget en modo portable.

Archivos:
- config.json: Configuración del widget (posición, carpetas favoritas, etc.)

El widget creará automáticamente config.json cuando se ejecute por primera vez.
EOF

# Crear archivo de información en logs
cat > dist/logs/README.txt << 'EOF'
Este directorio contiene los logs del widget en modo portable.

Archivos:
- widget.log: Log de la aplicación con información de ejecución y errores

Los logs se crean automáticamente cuando el widget se ejecuta.
EOF

# Copiar el icono
cp ../icon.svg dist/

# Crear script de lanzamiento (por si hay problemas con el ejecutable)
echo "📄 Creando script de respaldo..."
cat > dist/run-widget.sh << 'EOF'
#!/bin/bash
# Script de respaldo para ejecutar el widget
# Útil si el ejecutable de PyInstaller tiene problemas

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Verificar si hay un ejecutable de PyInstaller
if [ -f "$SCRIPT_DIR/nautilus-vscode-widget-portable" ]; then
    echo "🚀 Ejecutando versión compilada..."
    "$SCRIPT_DIR/nautilus-vscode-widget-portable"
else
    echo "❌ No se encuentra el ejecutable compilado"
    echo "📝 Ejecutando script Python directamente..."
    python3 "$SCRIPT_DIR/../nautilus-vscode-widget.py"
fi
EOF

chmod +x dist/run-widget.sh

# Crear README
echo "📝 Creando documentación..."
cat > dist/README-PORTABLE.md << 'EOF'
# Nautilus VSCode Widget - Versión Portable con PyInstaller

## 🎯 ¿Qué es esta versión?

Un **ejecutable autónomo** que incluye todas las dependencias necesarias. El usuario puede ejecutarlo directamente sin necesidad de instalar Python ni ninguna dependencia.

## 🚀 Uso Inmediato

### Ejecutar el programa:
```bash
./nautilus-vscode-widget-portable
```

### Si hay problemas con el ejecutable:
```bash
./run-widget.sh
```

## 📁 Estructura del Paquete Portable

```
nautilus-vscode-widget-portable/
├── nautilus-vscode-widget-portable  # Ejecutable principal
├── run-widget.sh                    # Script de respaldo
├── icon.svg                         # Icono del programa
├── conf/                            # Configuración (portable)
│   ├── config.json                  # Se crea automáticamente
│   └── README.txt
├── logs/                            # Logs de la aplicación
│   ├── widget.log                   # Se crea automáticamente
│   └── README.txt
└── README-PORTABLE.md               # Esta documentación
```

### ⚠️ IMPORTANTE: Carpetas Portable

Esta versión portable guarda **toda la configuración en la carpeta local**:
- **conf/config.json**: Tu configuración, posición del widget, carpetas favoritas
- **logs/widget.log**: Logs de ejecución

**Ventajas:**
- ✅ Puedes mover toda la carpeta a otro lugar o PC
- ✅ Tu configuración viaja con el ejecutable
- ✅ No deja rastros en el sistema

**Nota sobre Autostart:**
- El autostart SÍ se guarda en el sistema (`~/.config/autostart/`)
- Esto es necesario para que funcione al iniciar sesión
- Si mueves la carpeta, debes reconfigurar el autostart

## 🎨 Características

- ✅ **Ejecutable autónomo** - No requiere Python instalado
- ✅ **Incluye todas las dependencias** - GTK, Xlib, etc.
- ✅ **Verdaderamente portable** - Configuración en carpeta local
- ✅ **Compatible con Ubuntu/Debian** - Probado en sistemas Linux
- ✅ **Mismas funcionalidades** - Todas las características de la versión original

## 🔧 Para Desarrolladores

### Compilar nueva versión:
```bash
cd linux-portable/
./build-pyinstaller.sh
```

### Requisitos de compilación:
- Python 3
- PyInstaller: `pip install pyinstaller`
- Dependencias de desarrollo: `sudo apt install python3-dev`

## 🐛 Solución de Problemas

### Error: "No se puede ejecutar el binario"
- Verifica que el archivo tenga permisos de ejecución: `chmod +x nautilus-vscode-widget-portable`
- Usa el script de respaldo: `./run-widget.sh`

### El widget no aparece
- Verifica que Nautilus esté ejecutándose
- Asegúrate de que Nautilus esté en foco (ventana activa)

### Problemas con GTK
- Si hay errores de GTK, usa el script de respaldo que ejecuta Python directamente

### La configuración no se guarda
- Verifica que la carpeta `conf/` tenga permisos de escritura
- Revisa el archivo `logs/widget.log` para ver errores

---

**Versión: 3.3.0 Portable (PyInstaller)**
**Compilado con PyInstaller - Incluye todas las dependencias**
**Configuración portable en carpeta local**
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     ¡Ejecutable PyInstaller Creado Exitosamente!            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Archivos generados en: ./dist/"
echo ""
echo "📁 Estructura portable creada:"
echo "   ├── nautilus-vscode-widget-portable (ejecutable)"
echo "   ├── run-widget.sh (script de respaldo)"
echo "   ├── conf/ (configuración portable)"
echo "   ├── logs/ (logs de ejecución)"
echo "   ├── icon.svg"
echo "   └── README-PORTABLE.md"
echo ""
echo "🎯 Para usar:"
echo "   1. Copia la carpeta 'dist/' a cualquier ubicación"
echo "   2. Renombra 'dist/' a 'nautilus-vscode-widget-portable/'"
echo "   3. Ejecuta: ./nautilus-vscode-widget-portable"
echo ""
echo "💡 Características de la versión portable:"
echo "   ✅ Incluye TODAS las dependencias (Python, GTK, Xlib, etc.)"
echo "   ✅ Configuración en carpeta local (conf/config.json)"
echo "   ✅ Logs en carpeta local (logs/widget.log)"
echo "   ✅ Puedes mover toda la carpeta a otro PC"
echo ""
echo "✨ ¡El usuario puede ejecutarlo sin instalar nada!"
