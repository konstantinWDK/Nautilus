# Nautilus VSCode Widget - Botón Flotante Inteligente

[![Version](https://img.shields.io/badge/version-3.3.6-blue.svg)](https://github.com/konstantinWDK/nautilus-vscode-widget)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Un botón flotante elegante y moderno que te permite abrir carpetas de Nautilus directamente en VSCode con un solo click. Aparece solo cuando lo necesitas.

> **📢 Nueva versión 3.3.6**: Instalador mejorado - versión estable y confiable. Ver [CHANGELOG.md](CHANGELOG.md) para detalles.

## ✨ Características Principales

- **Aparición Inteligente**: Solo se muestra cuando Nautilus está en foco (o siempre si lo prefieres)
- **Carpetas Favoritas**: Añade y accede rápidamente a tus carpetas favoritas con diseño minimalista
  - Botón "+" verde flotante sin fondo para añadir favoritos
  - Círculos oscuros semi-transparentes con iniciales para cada carpeta
- **Transparencia Circular**: Diseño circular perfecto sin fondo cuadrado
- **Ultra Compacto**: Solo **36x36 píxeles** de diseño minimalista
- **Detección Avanzada**: Múltiples métodos (DBus, xdotool, wmctrl) para detectar carpetas
- **Tema Oscuro Moderno**: Menús y diálogos con diseño elegante
- **Totalmente Configurable**: Color del botón, comando del editor, visibilidad y más
- **Inicio Automático**: Opción para iniciar con el sistema
- **Arrastrable**: Mueve el botón a cualquier posición de la pantalla

## 🎨 Diseño

- **Forma**: Círculo perfecto de 36x36 píxeles
- **Fondo**: Completamente transparente (sin cuadrado visible)
- **Botón**: Alta opacidad (95%) con borde visible
- **Icono**: Logo de VSCode de 24x24 píxeles
- **Sombras**: Efectos de sombra modernos para profundidad
- **Tema oscuro**: Menús y diálogos con diseño oscuro elegante

## 🚀 Instalación

### Opción 1: Paquete .deb (Recomendado para Ubuntu/Debian)

Descarga el archivo `.deb` desde [Releases](https://github.com/konstantinWDK/nautilus-vscode-widget/releases) e instálalo:

#### ⚠️ IMPORTANTE: Usa apt install, NO dpkg -i

**Método CORRECTO (RECOMENDADO) - Instala dependencias automáticamente:**
```bash
# ✅ ESTE MÉTODO SÍ INSTALA LAS DEPENDENCIAS AUTOMÁTICAMENTE
sudo apt install ./nautilus-vscode-widget_3.3.6_all.deb
```

**Método INCORRECTO - NO instala dependencias:**
```bash
# ❌ ESTE MÉTODO NO INSTALA LAS DEPENDENCIAS
sudo dpkg -i nautilus-vscode-widget_3.3.6_all.deb
```

#### Método Gráfico
- Haz doble clic en el archivo `.deb` 
- Se abrirá el Centro de Software de Ubuntu (o tu gestor de paquetes)
- Haz clic en "Instalar"
- **Las dependencias se instalarán automáticamente**

#### Si ya usaste dpkg -i y falló:
```bash
# 1. Reparar la instalación
sudo apt install -f

# 2. Instalar correctamente
sudo apt install ./nautilus-vscode-widget_3.3.6_all.deb
```

### Opción 2: Desde el repositorio

```bash
# Clonar el repositorio
git clone https://github.com/konstantinWDK/nautilus-vscode-widget.git
cd nautilus-vscode-widget

# Ejecutar el script de instalación
chmod +x install.sh
./install.sh
```

### Opción 3: Compilar el paquete .deb

```bash
# Desde el repositorio clonado
cd linux
./build-deb.sh

# Instalar el paquete generado (las dependencias se instalarán automáticamente)
sudo apt install ../dist/nautilus-vscode-widget_3.3.0_all.deb
```

### ✅ Verificación de Instalación

Después de instalar, verifica que todo funciona:

```bash
# Verificar que el programa está instalado
which nautilus-vscode-widget

# Verificar que las dependencias están instaladas
dpkg -l | grep -E "(python3-gi|python3-xlib|xdotool|wmctrl)"

# Iniciar el widget
nautilus-vscode-widget
```

### 📦 Gestión de Dependencias

**Las dependencias se instalarán automáticamente** cuando uses:
- `sudo apt install ./nautilus-vscode-widget_3.3.0_all.deb` (RECOMENDADO)
- O el gestor gráfico de paquetes (doble clic en el .deb)

El sistema de paquetes Debian/Ubuntu maneja automáticamente las dependencias especificadas en el archivo `control` del paquete.

#### Dependencias que se instalarán automáticamente:
- **python3** - Intérprete de Python 3
- **python3-gi** - Bindings de Python para GTK
- **python3-gi-cairo** - Soporte Cairo para GTK
- **gir1.2-gtk-3.0** - Introspection data para GTK 3
- **python3-xlib** - Biblioteca para operaciones X11 nativas (NUEVO en v3.3.0)
- **xdotool** - Herramienta para manipular ventanas X11
- **wmctrl** - Controlador de ventanas X11

#### Comandos útiles para gestión:
```bash
# Verificar dependencias instaladas
dpkg -l | grep -E "(python3-gi|python3-xlib|xdotool|wmctrl)"

# Desinstalar completamente
sudo apt remove nautilus-vscode-widget

# Verificar que no hay procesos ejecutándose
ps aux | grep nautilus-vscode-widget
```

## 📖 Uso

### Iniciar la aplicación

**Método 1: Desde el menú de aplicaciones**
1. Busca "Nautilus VSCode Widget" en tu menú de aplicaciones
2. Haz click para iniciar

**Método 2: Desde terminal**
```bash
# Si instalaste con .deb o install.sh
nautilus-vscode-widget

# O directamente desde el repositorio
./run.sh
```

### Interacción con el widget

**Botón principal:**
- **Click izquierdo**: Abre la carpeta actual de Nautilus en VSCode
- **Click derecho**: Muestra menú de configuración
- **Arrastrar**: Mueve el botón a otra posición (mantén presionado y arrastra)

**Carpetas favoritas:**
- **Botón "+"**: Símbolo verde flotante sin fondo, aparece arriba del botón principal
- **Botones de carpetas**: Círculos oscuros semi-transparentes con la inicial de la carpeta
- **Click en favorito**: Abre directamente esa carpeta en VSCode
- **Click derecho en favorito**: Eliminar de favoritos
- **Hover**: Efecto de brillo al pasar el mouse sobre los botones

## ⚙️ Configuración

Accede a la configuración haciendo click derecho sobre el botón:

1. **Comando del editor**: Cambia el comando para abrir VSCode (por defecto: `code`)
2. **Color del botón**: Personaliza el color del círculo
3. **Mostrar etiqueta**: Activa/desactiva una pequeña etiqueta (desactivada por defecto)
4. **Iniciar con el sistema**: El botón aparecerá automáticamente al iniciar sesión
5. **Mostrar siempre**: El widget estará visible siempre, no solo cuando Nautilus está activo

### Configuración del Inicio Automático

Para habilitar el inicio automático:
1. Click derecho en el botón → ⚙️ Configuración
2. Activa el interruptor "Iniciar con el sistema"
3. Guarda los cambios

Esto creará un archivo `.desktop` en `~/.config/autostart/`

## 🎯 Comportamiento Visual

### Estados de Visibilidad
- **Modo Normal (por defecto)**:
  - Visible cuando Nautilus está activo/en foco Y hay un directorio válido
  - Invisible cuando otra aplicación está activa
- **Modo Siempre Visible**:
  - Widget visible permanentemente (activar en configuración)
  - Útil si trabajas frecuentemente con VSCode

### Carpetas Favoritas
- **Botón "+"**: Símbolo verde (#78DC78) sin fondo circular, flotante y minimalista
- **Botones de carpetas**: Círculos oscuros semi-transparentes (rgba(30, 30, 35, 0.85))
- **Identificación**: Cada botón muestra la inicial de la carpeta en blanco
- **Distribución**: Se muestran en columna vertical sobre el botón "+"
- **Diseño**: UI minimalista con efectos de hover y sombras suaves

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
~/.config/nautilus-vscode-widget/config.json
```

Archivo de autostart (si está habilitado):
```
~/.config/autostart/nautilus-vscode-widget.desktop
```

## 🔧 Requisitos

- Python 3
- GTK+ 3
- cairo (para transparencia)
- python-xlib (para detección nativa de ventanas)
- xdotool (para detección de ventanas - fallback)
- xprop (para propiedades de ventana - fallback)
- gdbus (para comunicación con Nautilus)
- VSCode o compatible (code, code-insiders, codium, vscodium)

Instalar dependencias en Ubuntu/Debian:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 python3-xlib xdotool x11-utils
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

### Versión 3.1.0 (Actual)
- 🎨 Diseño minimalista mejorado para carpetas favoritas
  - Botón "+" verde flotante sin fondo circular
  - Círculos oscuros semi-transparentes para favoritos
  - Centrado perfecto de texto en botones circulares
- 🐛 Corrección de advertencias de deprecación GTK3
- 🐛 Solucionado CSS global que afectaba Nautilus

### Versión 3.0
- ✨ Aparición inteligente: solo visible cuando Nautilus está enfocado
- 📁 Sistema de carpetas favoritas con acceso rápido
- 🎯 Modo "Mostrar siempre" opcional
- 🎨 Tema oscuro moderno en menús y diálogos
- 🔍 Detección mejorada con DBus
- 🚀 Código optimizado y compatibilidad GTK3 mejorada

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
