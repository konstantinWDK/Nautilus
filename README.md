# Floating VSCode Opener

Una aplicación con interfaz gráfica que muestra un botón flotante en tu escritorio de Ubuntu. El botón detecta automáticamente la carpeta que estás viendo en Nautilus y te permite abrirla en Visual Studio Code con un solo clic.

## Características

- Botón flotante circular que aparece sobre todas las ventanas
- Detecta automáticamente la carpeta activa en Nautilus
- Interfaz gráfica de configuración completa
- Diseño moderno con efectos visuales (hover, sombras, gradientes)
- Arrastrable - mueve el botón a donde quieras
- Menú contextual con opciones
- Inicio automático al iniciar sesión
- Totalmente personalizable (color, editor, etiquetas)
- Compatible con VSCode, VSCode Insiders y otros editores

## Vista Previa

El botón aparece como un círculo flotante azul en tu pantalla que puedes mover libremente. Cuando haces clic derecho, se abre un menú con opciones de configuración.

## Requisitos

- Ubuntu/Linux con entorno gráfico GNOME
- Python 3.6+
- Visual Studio Code (o cualquier otro editor)
- PyGObject (GTK+ 3)
- xdotool (para detectar ventanas activas)

## Instalación

### Instalación Rápida (Recomendada)

Ejecuta el script de instalación que configurará todo automáticamente:

```bash
cd "/home/wdk/Documentos/WEBMASTERK/Mis plugins/Nautilus"
./install.sh
```

El script:
1. Instala todas las dependencias necesarias (python3-gi, xdotool, etc.)
2. Configura la aplicación para inicio automático
3. Inicia la aplicación inmediatamente

### Instalación Manual

Si prefieres instalar paso a paso:

1. Instala las dependencias del sistema:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 xdotool
   pip3 install --user PyGObject
   ```

2. Da permisos de ejecución:
   ```bash
   chmod +x floating_button.py
   ```

3. Ejecuta la aplicación:
   ```bash
   python3 floating_button.py
   ```

### Ejecutar sin Instalar

Para probar la aplicación sin instalarla:

```bash
./run.sh
```

## Uso

### Uso Básico

1. La aplicación muestra un botón flotante circular en tu pantalla
2. Abre Nautilus y navega a cualquier carpeta
3. El botón detecta automáticamente la carpeta activa
4. Click izquierdo en el botón: Abre la carpeta en VSCode
5. Arrastra el botón para moverlo a cualquier posición

### Menú Contextual

Click derecho en el botón para acceder a:
- Configuración: Personaliza el comportamiento y apariencia
- Salir: Cierra la aplicación

### Configuración

La ventana de configuración te permite ajustar:

1. **Comando del editor**: Cambia entre VSCode, VSCode Insiders, u otro editor
   - `code` - VSCode estándar
   - `code-insiders` - VSCode Insiders
   - `subl` - Sublime Text
   - `atom` - Atom
   - Cualquier comando personalizado

2. **Color del botón**: Selector visual de color para personalizar la apariencia

3. **Mostrar etiqueta**: Activa/desactiva el texto "VSCode" en el botón

Todos los cambios se guardan automáticamente en `~/.config/nautilus-vscode-opener/config.json`

## Desinstalación

Ejecuta el script de desinstalación:

```bash
./uninstall.sh
```

Esto:
- Detiene la aplicación
- Elimina el acceso directo del menú de aplicaciones
- Deshabilita el inicio automático
- Opcionalmente elimina la configuración guardada

## Archivos del Proyecto

- **[floating_button.py](floating_button.py)** - Aplicación principal con GUI
- **[install.sh](install.sh)** - Script de instalación automática
- **[uninstall.sh](uninstall.sh)** - Script de desinstalación
- **[run.sh](run.sh)** - Script rápido para ejecutar sin instalar
- **[requirements.txt](requirements.txt)** - Dependencias de Python
- **[README.md](README.md)** - Este archivo

## Archivos de Configuración

La aplicación guarda su configuración en:
```
~/.config/nautilus-vscode-opener/config.json
```

Estructura del archivo de configuración:
```json
{
  "position_x": 100,
  "position_y": 100,
  "editor_command": "code",
  "button_color": "#007ACC",
  "show_label": true
}
```

Puedes editar este archivo manualmente o usar la GUI de configuración.

## Solución de Problemas

### El botón flotante no aparece

1. Verifica que la aplicación esté ejecutándose:
   ```bash
   ps aux | grep floating_button.py
   ```

2. Verifica que las dependencias estén instaladas:
   ```bash
   python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('OK')"
   ```

3. Ejecuta la aplicación manualmente para ver errores:
   ```bash
   python3 floating_button.py
   ```

4. Verifica que xdotool esté instalado:
   ```bash
   which xdotool
   ```

### El botón no detecta la carpeta de Nautilus

1. Verifica que Nautilus esté abierto y sea la ventana activa

2. El título de la ventana de Nautilus debe mostrar la ruta de la carpeta

3. Prueba ejecutando manualmente:
   ```bash
   xdotool getactivewindow getwindowname
   ```
   Debe mostrar el título de la ventana activa

4. En la configuración regional en español, Nautilus puede llamarse "Archivos" en lugar de "Files"

### VSCode no se abre

1. Verifica que VSCode esté instalado y el comando `code` esté disponible:
   ```bash
   which code
   ```

2. Si usas el .deb de VSCode, asegúrate de que `/usr/bin/code` esté en tu PATH

3. Si instalaste VSCode de forma manual, crea un enlace simbólico:
   ```bash
   sudo ln -s /ruta/a/vscode/bin/code /usr/local/bin/code
   ```

4. Cambia el comando del editor en la configuración (click derecho → Configuración)

### La aplicación no inicia automáticamente

1. Verifica que el archivo autostart exista:
   ```bash
   ls -la ~/.config/autostart/vscode-opener.desktop
   ```

2. Verifica el contenido del archivo:
   ```bash
   cat ~/.config/autostart/vscode-opener.desktop
   ```

3. Re-ejecuta el instalador:
   ```bash
   ./install.sh
   ```

## Cómo Funciona

1. **Detección de ventana activa**: Usa `xdotool` para obtener el título de la ventana activa
2. **Extracción de ruta**: Analiza el título de Nautilus para extraer la ruta de la carpeta
3. **Botón flotante**: Ventana GTK siempre visible sobre otras ventanas
4. **Persistencia**: Guarda posición y configuración en JSON
5. **Inicio automático**: Archivo .desktop en autostart

## Tecnologías Utilizadas

- **Python 3** - Lenguaje de programación
- **PyGObject (GTK+ 3)** - Interfaz gráfica
- **xdotool** - Detección de ventanas activas
- **JSON** - Almacenamiento de configuración
- **Bash** - Scripts de instalación

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Siéntete libre de:
- Reportar bugs
- Sugerir nuevas características
- Enviar pull requests
- Mejorar la documentación

## Autor

Desarrollado para facilitar el flujo de trabajo entre el explorador de archivos y el editor de código.
