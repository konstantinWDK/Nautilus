# Nautilus VSCode Opener - Botón Flotante Minimalista

Un botón flotante ultra-compacto y elegante que te permite abrir carpetas de Nautilus directamente en VSCode con un solo click.

## ✨ Características Principales

- **Ultra Compacto**: Diseño minimalista de solo **36x36 píxeles**
- **Círculo Oscuro Elegante**: Fondo oscuro (#2C2C2C) sin colores llamativos
- **Icono de VSCode**: Muestra el icono real de VSCode del sistema
- **Ocultación Inteligente**: Se desvanece suavemente cuando cambias a otra aplicación
- **Aparición Suave**: Aparece con animación fade cuando vuelves a Nautilus
- **Inicio Automático**: Opción configurable para iniciar con el sistema
- **Totalmente Configurable**: Color del botón, comando del editor, y más
- **Detección Automática**: Detecta la carpeta activa en Nautilus
- **Arrastrable**: Mueve el botón a cualquier posición de la pantalla

## 🎨 Diseño

- **Tamaño**: 36x36 píxeles (muy discreto)
- **Color por defecto**: Círculo oscuro (#2C2C2C)
- **Icono**: 24x24 píxeles del logo de VSCode
- **Sombra sutil**: Para destacar sobre cualquier fondo
- **Sin etiquetas**: Solo el icono para máxima limpieza visual

## 🚀 Instalación Rápida

```bash
# Ejecutar el script de instalación
chmod +x install.sh
./install.sh
```

Esto creará un acceso directo en tu menú de aplicaciones.

## 📖 Uso

### Método 1: Desde el menú de aplicaciones
1. Busca "Nautilus VSCode Opener" en tu menú de aplicaciones
2. Haz click para iniciar el botón flotante

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
2. **Color del botón**: Personaliza el color del círculo (por defecto: #2C2C2C - gris oscuro)
3. **Mostrar etiqueta**: Activa/desactiva una pequeña etiqueta (desactivada por defecto)
4. **Iniciar con el sistema**: El botón aparecerá automáticamente al iniciar sesión

### Configuración del Inicio Automático

Para habilitar el inicio automático:
1. Click derecho en el botón → Configuración
2. Activa el interruptor "Iniciar con el sistema"
3. Guarda los cambios

Esto creará un archivo `.desktop` en `~/.config/autostart/`

## 🎯 Comportamiento Visual

- **Opacidad 100%**: Cuando Nautilus está activo/en foco
- **Opacidad 0%**: Cuando otra aplicación está activa
- **Transición suave**: Animación de fade de 20ms entre estados
- **Hover effect**: El botón se ilumina ligeramente al pasar el mouse
- **Active effect**: Se oscurece al hacer click

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
- xdotool (para detección de ventanas)
- VSCode o compatible (code, code-insiders, codium, vscodium)

Instalar dependencias en Ubuntu/Debian:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 xdotool
```

## 🐛 Solución de Problemas

### El botón no aparece
- Verifica que Nautilus esté ejecutándose
- Comprueba que xdotool esté instalado: `which xdotool`
- El botón se oculta automáticamente cuando Nautilus no está en foco

### No detecta la carpeta correctamente
- El programa usa varios métodos para detectar la carpeta
- Si falla, usará la carpeta actual del sistema
- Puedes ver los logs ejecutando desde terminal

### VSCode no se abre
- Verifica que VSCode esté instalado: `which code`
- Puedes configurar una ruta personalizada en Configuración
- El programa intentará varios comandos comunes automáticamente

### Quiero cambiar el color del botón
- Click derecho → Configuración
- Selecciona el color que prefieras
- Guarda y reinicia la aplicación

## 💡 Tips

1. **Posición óptima**: Coloca el botón en una esquina de tu pantalla donde no moleste
2. **Color personalizado**: Si trabajas con temas claros, prueba un color más oscuro
3. **Inicio automático**: Actívalo si usas Nautilus frecuentemente
4. **Múltiples editores**: Puedes cambiar el comando para usar Sublime, Atom, etc.

## 🆕 Changelog

### Versión 2.0 (Actual)
- ✨ Reducido a 36x36 píxeles (ultra compacto)
- 🎨 Nuevo diseño: círculo oscuro sin fondo de color
- 🌓 Color por defecto cambiado a gris oscuro (#2C2C2C)
- 🔍 Icono reducido a 24x24 píxeles
- 🎯 Eliminado gradiente, diseño más limpio
- ⚡ Mejoras de rendimiento en animaciones

### Versión 1.0
- Botón flotante básico
- Detección de carpeta activa
- Configuración personalizable
- Inicio automático opcional

## 📝 Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo y compartirlo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Si encuentras algún bug o tienes alguna sugerencia:
1. Reporta el problema
2. Propón una mejora
3. Envía un pull request

---

**Nota**: Este es un proyecto independiente y no está afiliado con Microsoft o el proyecto VSCode.
