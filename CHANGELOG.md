# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [3.1.0] - 2025-01-XX

### ✨ Añadido

#### Carpetas Favoritas
- **Botón "+" flotante**: Símbolo verde sin fondo para añadir carpetas favoritas
- **Botones de favoritos**: Círculos oscuros semi-transparentes con iniciales blancas
- **Diseño minimalista**: UI limpia y elegante con efectos de hover
- **Acceso rápido**: Click en favoritos para abrir carpetas directamente en VSCode
- **Gestión fácil**: Click derecho para eliminar favoritos

### ⚡ Mejorado

#### Interfaz de Usuario - Favoritos
- **Centrado perfecto**: Labels centrados con Gtk.Box para alineación precisa
- **Tamaños optimizados**: Botón "+" de 24px, favoritos de 28px
- **Botón "+" sin fondo**: Símbolo verde (#78DC78) flotante y minimalista, sin círculo
- **Favoritos oscuros**: Círculos semi-transparentes (rgba(30, 30, 35, 0.85))
- **Hover mejorado**: Resplandor verde suave en el "+" al pasar el mouse

### 🐛 Corregido

#### Problemas Visuales
- **Advertencias de deprecación**: Suprimidas advertencias de `Gtk.Window.set_opacity`
- **Centrado de texto**: Corregido centrado de símbolos "+" e iniciales en círculos
- **CSS global**: Solucionado problema de CSS afectando otras aplicaciones (Nautilus)

---

## [3.0.0] - 2025-01-XX

### ✨ Añadido

#### Aparición Inteligente
- **Visibilidad contextual**: El botón ahora solo aparece cuando Nautilus está enfocado
- **Detección de foco**: Verifica cada 200ms si Nautilus es la ventana activa
- **Validación de directorio**: Solo se muestra si hay un directorio válido detectado
- **Ocultar automático**: Se desvanece al cambiar a otras aplicaciones (VSCode, navegador, etc.)

#### Transparencia Circular Perfecta
- **Región circular**: Implementación de `shape_combine_region` para forma circular
- **Input shape**: El área de click es exactamente circular
- **Sin fondo cuadrado**: Eliminado completamente el fondo rectangular
- **Cairo rendering**: Uso de Cairo para transparencia total del fondo

#### Detección Mejorada de Directorios
- **Método DBus**: Consulta directa a Nautilus vía DBus (método más confiable)
- **Múltiples fallbacks**: 7 métodos diferentes de detección en cascada
- **Búsqueda recursiva**: Busca carpetas por nombre en ubicaciones comunes
- **Soporte multi-idioma**: Detecta nombres de carpetas en español e inglés

#### Tema Oscuro Moderno
- **Menús oscuros**: Fondo oscuro elegante (`rgba(35, 35, 35, 0.98)`)
- **Diálogos oscuros**: Tema oscuro consistente en todas las ventanas
- **Texto legible**: Color blanco en todas las etiquetas y controles
- **Inputs oscuros**: Campos de entrada con fondo oscuro y texto blanco
- **Botones estilizados**: Botones con diseño moderno y hover effects

### ⚡ Mejorado

#### Rendimiento
- **Animación 2x más rápida**: De ~1 segundo a ~375ms
- **Incremento de opacidad**: Aumentado de 0.1 a 0.2 por frame
- **Intervalo reducido**: De 20ms a 15ms entre frames
- **Sin logs de debug**: Eliminados todos los prints innecesarios
- **Código optimizado**: Reducción de llamadas a subprocess

#### Interfaz de Usuario
- **Opacidad del botón**: Aumentada de 0.75 a 0.95 para mejor visibilidad
- **Borde más visible**: De 1px a 2px con mayor transparencia
- **Sombras mejoradas**: Sombras más pronunciadas para mejor profundidad
- **Hover effect mejorado**: Mayor contraste al pasar el mouse

#### Detección de Ventanas
- **Uso de xprop**: Cambio de `xdotool getwindowclassname` a `xprop` para mayor fiabilidad
- **Manejo de errores**: Mejor gestión de fallos en detección de ventanas
- **Timeout consistente**: Timeouts uniformes de 1-2 segundos en todas las operaciones

### 🔧 Cambiado

#### Configuración Visual
- **Color por defecto**: Mantenido en `#2C2C2C` (gris oscuro)
- **Diseño del botón**: Círculo perfecto sin artefactos visuales
- **Posición inicial**: Primera ejecución en esquina inferior derecha

#### Comportamiento
- **Estado inicial**: Botón invisible hasta que Nautilus se enfoque
- **Opacidad inicial**: Comienza en 0.0 en lugar de 1.0
- **Transiciones**: Siempre animadas, nunca apariciones bruscas

### 🐛 Corregido

#### Problemas Visuales
- **Fondo cuadrado eliminado**: Solución completa del problema de fondo rectangular
- **Transparencia perfecta**: Uso de Cairo para fondo completamente transparente
- **Forma circular**: Aplicación correcta de región circular a la ventana

#### Problemas de Detección
- **Detección de foco**: Ahora detecta correctamente cuando Nautilus está enfocado
- **Detección de directorio**: Múltiples métodos garantizan mejor tasa de éxito
- **Nautilus sin título**: Soporte para versiones de Nautilus que no muestran rutas en títulos

#### Problemas de Rendimiento
- **Logs eliminados**: Reducción drástica de I/O en consola
- **Excepciones silenciadas**: Mejor manejo de errores sin spam de mensajes
- **Optimización de loops**: Menor uso de CPU en estado inactivo

### 🗑️ Eliminado

#### Mensajes de Debug
- Eliminado: `print(f"[DEBUG] ...")`
- Eliminado: `print(f"✓ Mostrando botón ...")`
- Eliminado: `print(f"✗ Ocultando botón ...")`
- Eliminado: `print(f"Directorio detectado: ...")`
- Eliminado: `print(f"No se pudo extraer directorio ...")`
- Eliminado: Todos los prints informativos innecesarios

#### CSS No Soportado
- Eliminado: `transform: scale(...)` (no soportado en GTK3)
- Eliminado: `backdrop-filter: blur(...)` (no soportado en GTK3)

#### Código Redundante
- Limpieza de código duplicado
- Eliminación de comentarios obsoletos
- Simplificación de manejo de excepciones

---

## [2.0.0] - 2024-XX-XX

### Añadido
- Diseño ultra compacto de 36x36 píxeles
- Círculo oscuro elegante con color configurable
- Sistema de configuración JSON
- Inicio automático opcional
- Detección multi-método de directorios

### Cambiado
- Tamaño reducido a 36x36 píxeles (antes era más grande)
- Color por defecto a gris oscuro `#2C2C2C`
- Icono reducido a 24x24 píxeles
- Diseño más limpio sin gradientes

---

## [1.0.0] - 2024-XX-XX

### Añadido
- Botón flotante básico
- Detección de carpeta activa en Nautilus
- Click para abrir en VSCode
- Drag & drop para reposicionar
- Configuración básica
- Menú contextual con click derecho

### Características Iniciales
- Detección automática de Nautilus
- Apertura rápida en VSCode
- Ventana flotante siempre visible
- Guardado de posición

---

## Tipos de Cambios

- `✨ Añadido` para nuevas funcionalidades
- `⚡ Mejorado` para cambios en funcionalidades existentes
- `🔧 Cambiado` para cambios que no son mejoras ni correcciones
- `🐛 Corregido` para corrección de bugs
- `🗑️ Eliminado` para funcionalidades eliminadas
- `🔒 Seguridad` para vulnerabilidades corregidas

---

## Formato de Versión

Usamos [Versionado Semántico](https://semver.org/lang/es/):
- **MAJOR** (X.0.0): Cambios incompatibles en la API
- **MINOR** (0.X.0): Nuevas funcionalidades compatibles
- **PATCH** (0.0.X): Correcciones de bugs compatibles

---

**Nota**: Las fechas se actualizarán cuando se publiquen las versiones oficiales.
