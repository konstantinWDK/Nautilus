# Nautilus VSCode Widget - Versión Portable con PyInstaller

## 🎯 ¿Qué es esta versión?

Un **ejecutable autónomo compilado con PyInstaller** que incluye **todas las dependencias necesarias** (Python, GTK, Xlib, etc.). El usuario puede ejecutarlo directamente **sin necesidad de instalar Python ni ninguna dependencia**.

## 🚀 Uso Inmediato

### Paso 1: Descargar
Descarga la carpeta completa `dist/` y guárdala en cualquier ubicación (Escritorio, Documentos, etc.)

### Paso 2: Ejecutar
```bash
cd dist/
./nautilus-vscode-widget-portable
```

### Si hay problemas:
```bash
./run-widget.sh
```

## 📁 Contenido del Paquete

```
dist/
├── nautilus-vscode-widget-portable    # Ejecutable compilado (115MB)
├── run-widget.sh                      # Script de respaldo
├── icon.svg                           # Icono del programa
└── README-PORTABLE.md                 # Documentación detallada
```

## 🎨 Características

- ✅ **Ejecutable autónomo** - No requiere Python instalado
- ✅ **Incluye TODAS las dependencias** - Python, GTK, Xlib, Cairo, etc.
- ✅ **No requiere instalación** - Ejecutar y listo
- ✅ **Compatible con Ubuntu/Debian** - Probado en sistemas Linux
- ✅ **Mismas funcionalidades** - Todas las características de la versión original
- ✅ **Portable** - Puedes mover la carpeta a otro equipo

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

### Tamaño del ejecutable:
- **115MB** - Incluye Python, GTK, Xlib y todas las dependencias
- Esto es normal para aplicaciones GTK compiladas con PyInstaller

## 🆚 Comparación: Portable vs .deb

| Característica | Versión Portable | Versión .deb |
|----------------|------------------|--------------|
| Instalación | No requiere | Requiere instalación |
| Dependencias | Incluidas en el ejecutable | Se instalan con el paquete |
| Tamaño | 115MB (todo incluido) | ~24KB + dependencias del sistema |
| Portabilidad | Alta (mover carpeta) | Baja (instalado en sistema) |
| Usuario | Ejecutar directamente | `sudo apt install` |

## 💡 Casos de Uso Recomendados

### Para usuarios finales:
- **Usa la versión portable** si quieres probar el programa sin instalar nada
- **Usa la versión .deb** si quieres una instalación permanente en el sistema

### Para distribuir:
- **Versión portable** - Para usuarios que no quieren instalar paquetes
- **Versión .deb** - Para instalación permanente en el sistema

## 🐛 Solución de Problemas

### Error: "No se puede ejecutar el binario"
```bash
chmod +x nautilus-vscode-widget-portable
```

### Error: "Comando no encontrado"
- Asegúrate de estar en la carpeta `dist/`
- Verifica que el archivo tenga permisos de ejecución

### El widget no aparece
- Verifica que Nautilus esté ejecutándose
- Asegúrate de que Nautilus esté en foco (ventana activa)
- Usa el script de respaldo: `./run-widget.sh`

### Problemas con GTK o dependencias
- Usa el script de respaldo que ejecuta Python directamente
- O instala las dependencias manualmente y usa el script Python original

## 📊 Detalles Técnicos

### Dependencias incluidas en el ejecutable:
- Python 3.12
- GTK+ 3
- Cairo
- Xlib
- PyGObject
- Todas las bibliotecas necesarias

### Compatibilidad:
- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ Sistemas con X11
- ✅ Escritorios GNOME

---

**Versión: 3.3.0 Portable (PyInstaller)**  
**Tamaño: 115MB (incluye todas las dependencias)**  
**Compilado con PyInstaller - ¡Ejecutar sin instalar nada!**
