# Nautilus VSCode Opener - Botón Flotante Inteligente

Un botón flotante elegante y moderno que te permite abrir carpetas de Nautilus directamente en VSCode con un solo click. Aparece solo cuando lo necesitas.

## ✨ Características Principales

- **Aparición Inteligente**: Solo se muestra cuando Nautilus está en foco
- **Transparencia Circular**: Diseño circular perfecto sin fondo cuadrado
- **Ultra Compacto**: Solo **36x36 píxeles** de diseño minimalista
- **Detección Avanzada**: Múltiples métodos (DBus, xdotool, wmctrl) para detectar carpetas
- **Animación Rápida**: Aparece/desaparece en menos de 400ms
- **Tema Oscuro Moderno**: Menús y diálogos con diseño elegante
- **Totalmente Configurable**: Color del botón, comando del editor, y más
- **Inicio Automático**: Opción para iniciar con el sistema
- **Arrastrable**: Mueve el botón a cualquier posición de la pantalla

## 🎨 Diseño

- **Forma**: Círculo perfecto de 36x36 píxeles
- **Fondo**: Completamente transparente (sin cuadrado visible)
- **Botón**: Alta opacidad (95%) con borde visible
- **Icono**: Logo de VSCode de 24x24 píxeles
- **Sombras**: Efectos de sombra modernos para profundidad
- **Tema oscuro**: Menús y diálogos con diseño oscuro elegante

## 🚀 Instalación Rápida

### Método 1: Script de instalación
```bash
# Ejecutar el script de instalación
chmod +x install.sh
./install.sh
```

Esto creará un acceso directo en tu menú de aplicaciones.

### Método 2: Instalación desde archivo .deb
Si tienes el archivo `.deb` en la carpeta `dist/`:

```bash
# Instalar desde el archivo .deb
sudo dpkg -i dist/nautilus-vscode-opener_3.0.0_all.deb
```

El programa se instalará automáticamente y estará disponible en tu menú de aplicaciones.

## 📖 Uso

### Método 1: Desde el menú de aplicaciones
1. Busca "Nautilus VSCode Opener" en tu menú de aplicaciones
2. Haz click para iniciar el botón flotante
3. El botón aparecerá **solo cuando Nautilus esté en foco**

### Método 2: Desde terminal
```bash
python3 floating_button.py
```

### Interacción con el botón

- **Click izquierdo**: Abre la carpeta actual en VSCode
- **Click derecho**: Muestra menú de configuración
- **Arrastrar**: Mueve el botón a otra posición (mantén presionado y arrastra)

## ⚙️ Configuración

Accede a la configuración haciendo click derecho sobre el botón:

1. **Comando del editor**: Cambia el comando para abrir VSCode (por defecto: `code`)
2. **Color del botón**: Personaliza el color del círculo
3. **Mostrar etiqueta**: Activa/desactiva una pequeña etiqueta (desactivada por defecto)
4. **Iniciar con el sistema**: El botón aparecerá automáticamente al iniciar sesión

### Configuración del Inicio Automático

Para habilitar el inicio automático:
1. Click derecho en el botón → ⚙️ Configuración
2. Activa el interruptor "Iniciar con el sistema"
3. Guarda los cambios

Esto creará un archivo `.desktop` en `~/.config/autostart/`

## 🎯 Comportamiento Visual

### Estados de Visibilidad
- **Visible (100% opacidad)**: Cuando Nautilus está activo/en foco Y hay un directorio válido
- **Invisible (0% opacidad)**: Cuando otra aplicación está activa (VSCode, navegador, etc.)
- **Transición**: Animación suave de fade in/out de ~375ms

### Efectos Interactivos
- **Hover**: El botón aumenta brillo y sombra al pasar el mouse
- **Click**: Se oscurece ligeramente al hacer click
- **Bordes**: Borde de 2px con transparencia para mejor definición

## 🔍 Detección de Directorios

El programa usa múltiples métodos para detectar la carpeta activa:

1. **DBus** (más confiable): Consulta directamente a Nautilus vía DBus
2. **Ventana activa**: Detecta la ventana enfocada de Nautilus
3. **Título de ventana**: Extrae la ruta del título de la ventana
4. **Propiedades de ventana**: Lee propiedades WM_NAME y _NET_WM_NAME
5. **Búsqueda por nombre**: Busca carpetas por nombre en ubicaciones comunes
6. **Fallback**: Usa el directorio actual como último recurso

## 📁 Archivos de Configuración

El programa guarda su configuración en:
```
~/.config/nautilus-vscode-opener/config.json
```

Archivo de autostart (si está habilitado):
```
~/.config/autostart/nautilus-vscode-opener.desktop
```

## 🔧 Requisitos

- Python 3
- GTK+ 3
- cairo (para transparencia)
- xdotool (para detección de ventanas)
- xprop (para propiedades de ventana)
- gdbus (para comunicación con Nautilus)
- VSCode o compatible (code, code-insiders, codium, vscodium)

Instalar dependencias en Ubuntu/Debian:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 xdotool x11-utils
```

## 🐛 Solución de Problemas

### El botón no aparece
- Verifica que Nautilus esté ejecutándose
- Asegúrate de que Nautilus esté **en foco** (ventana activa)
- Comprueba que xdotool esté instalado: `which xdotool`
- Verifica que haya un directorio válido detectado

### El botón aparece muy lento
- La animación de fade toma ~375ms, es normal
- Si parece más lento, verifica el rendimiento del sistema
- Puedes ejecutar desde terminal para ver logs de debug

### No detecta la carpeta correctamente
- El programa usa múltiples métodos de detección
- Prueba navegando a una carpeta diferente en Nautilus
- Algunas versiones de Nautilus no muestran rutas en títulos
- El método DBus es el más confiable en versiones modernas

### VSCode no se abre
- Verifica que VSCode esté instalado: `which code`
- Puedes configurar una ruta personalizada en Configuración → Comando del editor
- El programa intentará varios comandos comunes automáticamente

### El círculo tiene un fondo cuadrado
- Esto no debería ocurrir en la versión 3.0
- Verifica que tienes composición de ventanas habilitada en tu escritorio
- Algunas configuraciones de X11 pueden requerir composición

### Los menús aparecen con fondo blanco
- La versión 3.0 usa tema oscuro por defecto
- Si ves fondos blancos, reinicia la aplicación
- Verifica que estés usando la versión más reciente

## 💡 Tips

1. **Posición óptima**: Coloca el botón en una esquina donde no obstruya tu trabajo
2. **Multi-pantalla**: El botón funciona perfectamente en configuraciones multi-monitor
3. **Inicio automático**: Actívalo si usas Nautilus frecuentemente
4. **Múltiples editores**: Cambia el comando para usar Sublime, Atom, o cualquier editor
5. **Color personalizado**: Ajusta el color del botón para que combine con tu tema

## 📊 Rendimiento

- **Uso de CPU**: Mínimo (~0.1% en reposo)
- **Memoria**: ~30-40 MB
- **Intervalo de detección**:
  - Directorio: cada 500ms
  - Foco de ventana: cada 200ms
- **Sin logs**: Versión optimizada sin mensajes de debug

## 🆕 Últimos Cambios

Para ver el historial completo de cambios, consulta [CHANGELOG.md](CHANGELOG.md)

### Versión 3.0 (Actual)
- ✨ Aparición inteligente: solo visible cuando Nautilus está enfocado
- 🎯 Transparencia circular perfecta sin fondo cuadrado
- ⚡ Animación 2x más rápida (~375ms)
- 🎨 Tema oscuro moderno en menús y diálogos
- 🔍 Detección mejorada con DBus
- 🚀 Código optimizado sin mensajes de debug

## 📝 Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo y compartirlo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si encuentras algún bug o tienes alguna sugerencia:
1. Reporta el problema con detalles
2. Propón mejoras o nuevas características
3. Envía un pull request

## 🙏 Agradecimientos

- Proyecto VSCode por el excelente editor
- Comunidad GNOME por Nautilus
- Usuarios que han probado y dado feedback

---

**Nota**: Este es un proyecto independiente y no está afiliado con Microsoft o el proyecto VSCode.
