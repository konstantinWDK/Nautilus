#!/usr/bin/env python3
"""
Floating Button Application
Una aplicación con botón flotante que detecta la carpeta activa en Nautilus
y permite abrirla en VSCode
"""

# Version
VERSION = "3.3.9"

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import os
import re
import json
import time
import logging
import logging.handlers
import sys
import shutil
import threading
import platform
from functools import lru_cache
from datetime import datetime

# Importaciones opcionales según el entorno
try:
    from Xlib import display, X
    from Xlib.protocol import rq
    XLIB_AVAILABLE = True
except ImportError:
    XLIB_AVAILABLE = False


# OPTIMIZACIÓN: SubprocessCache reemplazada por functools.lru_cache
# Mucho más eficiente, sin timers, implementada en C
# La clase anterior tenía problemas de:
# - Timer innecesario cada 30s
# - Medición de memoria imprecisa
# - Código complejo y difícil de mantener

# El cache ahora se implementa directamente con decoradores @lru_cache
# en las funciones que necesitan caching


def setup_advanced_logging(log_dir):
    """
    Sistema de logging optimizado y profesional con:
    - Rotación automática de logs
    - Múltiples niveles de detalle
    - Diagnóstico completo de sistema
    - Detección de dependencias
    - Formato estructurado
    """
    log_file = os.path.join(log_dir, 'widget.log')
    debug_log_file = os.path.join(log_dir, 'widget_debug.log')

    # Crear directorio si no existe
    os.makedirs(log_dir, mode=0o700, exist_ok=True)

    # Logger principal
    logger = logging.getLogger('NautilusVSCodeWidget')
    logger.setLevel(logging.DEBUG)  # Capturar todo

    # Limpiar handlers existentes
    logger.handlers.clear()

    # 1. Handler para archivo principal (INFO y superior) con rotación
    main_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    main_handler.setLevel(logging.INFO)
    main_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main_handler.setFormatter(main_formatter)
    logger.addHandler(main_handler)

    # 2. Handler para debug (TODO) con rotación más agresiva
    debug_handler = logging.handlers.RotatingFileHandler(
        debug_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=2,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s:%(funcName)s:%(lineno)d\n'
        '    %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)

    # 3. Handler para consola (WARNING y superior)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_system_diagnostics(logger):
    """Registrar información completa del sistema para diagnóstico"""

    logger.info("=" * 80)
    logger.info(f"NAUTILUS VSCODE WIDGET v{VERSION} - INICIO")
    logger.info("=" * 80)

    # 1. Información del sistema
    logger.info("INFORMACIÓN DEL SISTEMA:")
    logger.info(f"  OS: {platform.system()} {platform.release()}")
    logger.info(f"  Versión: {platform.version()}")
    logger.info(f"  Arquitectura: {platform.machine()}")
    logger.info(f"  Python: {sys.version.split()[0]}")
    logger.info(f"  Ejecutable: {sys.executable}")
    logger.info(f"  Modo: {'Portable (PyInstaller)' if is_portable_mode() else 'Instalado'}")

    # 2. Variables de entorno importantes
    logger.info("\nVARIABLES DE ENTORNO:")
    env_vars = [
        'XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION', 'XDG_SESSION_TYPE',
        'WAYLAND_DISPLAY', 'DISPLAY', 'GDMSESSION', 'PATH'
    ]
    for var in env_vars:
        value = os.environ.get(var, '<no definida>')
        if var == 'PATH':
            # PATH puede ser muy largo, truncar
            value = value[:100] + '...' if len(value) > 100 else value
        logger.info(f"  {var}: {value}")

    # 3. Versiones de GTK
    logger.info("\nVERSIONES DE GTK:")
    try:
        logger.info(f"  GTK: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}")
        logger.info(f"  GDK: {Gdk.MAJOR_VERSION}.{Gdk.MINOR_VERSION}.{Gdk.MICRO_VERSION}")
        logger.info(f"  GLib: {GLib.MAJOR_VERSION}.{GLib.MINOR_VERSION}.{GLib.MICRO_VERSION}")
    except Exception as e:
        logger.error(f"  Error obteniendo versiones GTK: {e}")

    # 4. Dependencias opcionales
    logger.info("\nDEPENDENCIAS OPCIONALES:")

    # Xlib
    if XLIB_AVAILABLE:
        logger.info("  ✓ Xlib: Disponible")
    else:
        logger.warning("  ✗ Xlib: No disponible (opcional, usado para X11)")

    # Herramientas del sistema
    tools = {
        'xdotool': 'Detección de ventanas en X11',
        'wmctrl': 'Control de ventanas',
        'xprop': 'Propiedades de ventanas X11',
        'gdbus': 'Comunicación DBus con Nautilus',
        'nautilus': 'Gestor de archivos',
        'code': 'VSCode',
        'code-insiders': 'VSCode Insiders',
        'codium': 'VSCodium'
    }

    for tool, description in tools.items():
        path = shutil.which(tool)
        if path:
            logger.info(f"  ✓ {tool}: {path}")
        else:
            level = logging.WARNING if tool in ['gdbus', 'nautilus'] else logging.DEBUG
            logger.log(level, f"  ✗ {tool}: No encontrado - {description}")

    # 5. Detectar entorno gráfico
    env_info = detect_environment()
    logger.info("\nENTORNO GRÁFICO:")
    logger.info(f"  Servidor de display: {env_info['display_server'].upper()}")
    logger.info(f"  Desktop: {env_info['desktop'] or 'Desconocido'}")
    logger.info(f"  xdotool disponible: {'Sí' if env_info['has_xdotool'] else 'No'}")
    logger.info(f"  wmctrl disponible: {'Sí' if env_info['has_wmctrl'] else 'No'}")
    logger.info(f"  gdbus disponible: {'Sí' if env_info['has_gdbus'] else 'No'}")

    # 6. Verificar permisos y rutas
    logger.info("\nRUTAS Y PERMISOS:")
    config_dir = get_config_dir()
    log_dir = get_log_dir()
    logger.info(f"  Configuración: {config_dir}")
    logger.info(f"  Logs: {log_dir}")

    # Verificar permisos
    for path, name in [(config_dir, 'config'), (log_dir, 'logs')]:
        if os.path.exists(path):
            stat_info = os.stat(path)
            perms = oct(stat_info.st_mode)[-3:]
            logger.info(f"  Permisos {name}: {perms} (propietario: {stat_info.st_uid})")
        else:
            logger.warning(f"  {name}: No existe aún")

    # 7. Advertencias y recomendaciones
    logger.info("\nDIAGNÓSTICO:")

    if env_info['display_server'] == 'wayland':
        if not env_info['has_gdbus']:
            logger.warning("  ⚠ En Wayland sin gdbus, la detección de directorios puede fallar")
            logger.warning("    Instalar: sudo apt install libglib2.0-bin")
        else:
            logger.info("  ✓ Configuración óptima para Wayland")
    else:  # X11
        if not env_info['has_xdotool']:
            logger.warning("  ⚠ En X11 sin xdotool, la detección puede ser limitada")
            logger.warning("    Instalar: sudo apt install xdotool")
        else:
            logger.info("  ✓ Configuración óptima para X11")

    if not shutil.which('code') and not shutil.which('codium'):
        logger.warning("  ⚠ VSCode no detectado en PATH")
        logger.warning("    El widget intentará buscar en ubicaciones comunes")

    logger.info("=" * 80)
    logger.info("")


def detect_environment():
    """Detectar entorno de ejecución y herramientas disponibles"""
    env_info = {
        'display_server': 'x11',  # Default
        'desktop': os.environ.get('XDG_CURRENT_DESKTOP', '').lower(),
        'has_xdotool': shutil.which('xdotool') is not None,
        'has_wmctrl': shutil.which('wmctrl') is not None,
        'has_xprop': shutil.which('xprop') is not None,
        'has_gdbus': shutil.which('gdbus') is not None,
        'xlib_available': XLIB_AVAILABLE,
    }

    # Detectar Wayland
    if os.environ.get('WAYLAND_DISPLAY'):
        env_info['display_server'] = 'wayland'
    elif os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        env_info['display_server'] = 'wayland'

    return env_info


def validate_editor_command(cmd):
    """Validar que un comando de editor sea seguro y ejecutable con mejoras de seguridad"""
    if not cmd or not isinstance(cmd, str):
        return None

    # Remover espacios y validar que no contenga argumentos peligrosos
    cmd = cmd.strip()

    # NO permitir comandos con argumentos - solo el ejecutable
    # Los argumentos se añadirán de forma controlada al ejecutar
    if ' ' in cmd:
        # Si tiene espacios, solo tomar el primer elemento (el comando)
        cmd = cmd.split()[0]

    # Lista expandida de comandos peligrosos que no deberían ejecutarse
    dangerous_commands = {
        'rm', 'sudo', 'su', 'chmod', 'chown', 'dd', 'mkfs', 'fdisk',
        'shutdown', 'reboot', 'halt', 'poweroff', 'init', 'killall',
        'pkill', 'kill', 'systemctl', 'service', 'bash', 'sh', 'zsh',
        'python', 'perl', 'ruby', 'node', 'wget', 'curl', 'nc', 'netcat'
    }

    # Obtener nombre base del comando
    base_cmd = os.path.basename(cmd)

    # Verificar si el comando está en la lista de peligrosos
    if base_cmd in dangerous_commands or base_cmd.startswith('rm'):
        return None

    # Lista blanca de editores conocidos y seguros
    known_safe_editors = {
        'code', 'code-insiders', 'codium', 'vscodium',
        'vim', 'nvim', 'vi', 'nano', 'emacs', 'gedit', 'kate',
        'sublime_text', 'subl', 'atom', 'notepad++',
        'mousepad', 'pluma', 'xed', 'geany', 'brackets'
    }

    # Verificar si es una ruta absoluta
    if os.path.isabs(cmd):
        try:
            # Resolver symlinks para evitar ataques
            real_path = os.path.realpath(cmd)

            # Verificar que existe y es ejecutable
            if not (os.path.isfile(real_path) and os.access(real_path, os.X_OK)):
                return None

            # Verificar que el archivo no sea demasiado grande (posible malware)
            file_size = os.path.getsize(real_path)
            if file_size > 500 * 1024 * 1024:  # Máximo 500MB
                return None

            # Verificar que el nombre base esté en la whitelist o sea un editor conocido
            if (base_cmd in known_safe_editors or
                any(editor in real_path.lower() for editor in known_safe_editors)):
                return real_path

            # Si está en directorios del sistema, rechazar si no está en whitelist
            system_dirs = ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/usr/local/bin/']
            if any(real_path.startswith(dir_path) for dir_path in system_dirs):
                return None

            # Para rutas fuera de directorios del sistema, verificar ownership
            stat_info = os.stat(real_path)
            if stat_info.st_uid == os.getuid():
                # Archivo pertenece al usuario actual - verificar permisos
                # Rechazar si otros tienen permisos de escritura (world-writable)
                if stat_info.st_mode & 0o002:
                    return None
                return real_path

        except (OSError, ValueError):
            return None
        return None

    # Buscar en PATH con validación de seguridad
    cmd_path = shutil.which(cmd)
    if cmd_path:
        try:
            real_path = os.path.realpath(cmd_path)

            # Verificar que existe y es ejecutable
            if not (os.path.isfile(real_path) and os.access(real_path, os.X_OK)):
                return None

            # Verificar tamaño
            file_size = os.path.getsize(real_path)
            if file_size > 500 * 1024 * 1024:  # Máximo 500MB
                return None

            # Verificar que esté en la whitelist de editores conocidos
            if (base_cmd in known_safe_editors or
                any(editor in real_path.lower() for editor in known_safe_editors)):
                return real_path

        except (OSError, ValueError):
            return None

    return None


def validate_directory(path):
    """Validar que una ruta sea un directorio válido y accesible con protección contra path traversal"""
    if not path or not isinstance(path, str):
        return None

    try:
        # Resolver symlinks y normalizar ruta
        real_path = os.path.realpath(path)

        # Verificar que existe y es directorio
        if not os.path.isdir(real_path):
            return None

        # Verificar permisos de lectura
        if not os.access(real_path, os.R_OK):
            return None

        # Protección contra acceso a directorios sensibles del sistema
        # Rechazar acceso directo a directorios críticos (no sus subdirectorios)
        forbidden_dirs = {
            '/root', '/etc', '/sys', '/proc', '/dev', '/boot',
            '/var/log', '/usr/sbin', '/sbin'
        }

        # Verificar si es exactamente uno de los directorios prohibidos
        if real_path in forbidden_dirs:
            return None

        # Verificar que el directorio está dentro de ubicaciones permitidas
        # Permitir: /home, /tmp, /var/tmp, /opt (común para software), /usr/local
        user_home = os.path.expanduser('~')
        allowed_prefixes = (
            user_home,  # Home del usuario
            '/tmp/', '/var/tmp/',  # Directorios temporales
            '/opt/',  # Software opcional
            '/usr/local/',  # Software local
            '/media/', '/mnt/',  # Medios montados
        )

        # Si la ruta comienza con algún prefijo permitido, está OK
        if any(real_path.startswith(prefix) or real_path == prefix.rstrip('/')
               for prefix in allowed_prefixes):
            return real_path

        # Si no está en prefijos permitidos, rechazar
        return None

    except (OSError, ValueError):
        return None


def is_valid_directory(path):
    """Helper rápido para verificar si una ruta es un directorio válido"""
    return path and os.path.exists(path) and os.path.isdir(path)


def is_portable_mode():
    """Detectar si se está ejecutando en modo portable (PyInstaller)"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_executable_dir():
    """Obtener el directorio del ejecutable (portable) o del script"""
    if is_portable_mode():
        # PyInstaller crea una carpeta temporal en sys._MEIPASS
        # pero queremos la ubicación del ejecutable
        return os.path.dirname(sys.executable)
    else:
        # Modo normal: directorio del script
        return os.path.dirname(os.path.abspath(__file__))


def get_config_dir():
    """Obtener directorio de configuración según el modo"""
    if is_portable_mode():
        # Modo portable: usar carpeta 'conf' junto al ejecutable
        config_dir = os.path.join(get_executable_dir(), 'conf')
    else:
        # Modo instalado: usar directorio estándar del sistema
        config_dir = os.path.expanduser('~/.config/nautilus-vscode-widget')

    # Crear el directorio si no existe con permisos seguros (solo usuario)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, mode=0o700, exist_ok=True)

    return config_dir


def get_log_dir():
    """Obtener directorio de logs según el modo"""
    if is_portable_mode():
        # Modo portable: usar carpeta 'logs' junto al ejecutable
        log_dir = os.path.join(get_executable_dir(), 'logs')
    else:
        # Modo instalado: usar directorio estándar del sistema
        log_dir = os.path.expanduser('~/.local/share/nautilus-vscode-widget')

    # Crear el directorio si no existe con permisos seguros (solo usuario)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o700, exist_ok=True)

    return log_dir


def get_autostart_file():
    """Obtener ruta del archivo de autostart según el modo"""
    if is_portable_mode():
        # En modo portable, el autostart funciona diferente
        # Usamos el archivo de autostart del sistema pero apuntando al ejecutable portable
        autostart_dir = os.path.expanduser('~/.config/autostart')
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)
        return os.path.join(autostart_dir, 'nautilus-vscode-widget.desktop')
    else:
        # Modo instalado normal
        autostart_dir = os.path.expanduser('~/.config/autostart')
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)
        return os.path.join(autostart_dir, 'nautilus-vscode-widget.desktop')


class FloatingButtonApp:
    def __init__(self):
        # Configurar rutas según el modo (portable o instalado)
        self.is_portable = is_portable_mode()
        self.config_file = os.path.join(get_config_dir(), 'config.json')
        self.setup_logging()
        self.load_config()

        # Detectar entorno de ejecución (v3.3.1)
        self.env = detect_environment()
        self.logger.info(f"Entorno detectado: {self.env['display_server']} - Desktop: {self.env['desktop']}")
        self.logger.info(f"Herramientas disponibles - xdotool: {self.env['has_xdotool']}, "
                        f"xlib: {self.env['xlib_available']}, gdbus: {self.env['has_gdbus']}")

        # Initialize variables FIRST
        self.current_directory = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_x = 0  # Posición inicial del arrastre
        self.drag_start_y = 0  # Posición inicial del arrastre
        self.window_opacity = 1.0
        self.is_nautilus_focused = False
        self.fade_timer = None
        self.favorite_buttons = []  # Lista de botones favoritos
        self.add_button = None  # Botón de añadir carpetas
        self.animation_timer = None
        self.favorite_buttons_visible = False
        self.expand_animation_progress = 0.0
        self.drag_update_pending = False  # Para throttle de actualización durante drag

        # Optimización: Cache ahora usa functools.lru_cache en funciones individuales
        # self.subprocess_cache eliminado - ya no es necesario
        self.focus_timer_id = None
        self.dir_timer_id = None
        # self.recent_activity eliminada - ya no se usa timer periódico de z-order
        self.last_directory_detection = 0  # Timestamp de última detección

        # CRÍTICO: No iniciar timers de detección - widget siempre visible
        self.check_focus_interval = 0
        self.update_dir_interval = 0

        # Lista de todos los timers activos para cleanup
        self.active_timers = []
        # Lock para operaciones thread-safe
        self.directory_lock = threading.Lock()
        # Lista de procesos iniciados
        self.launched_processes = []

        # Create floating button window
        self.window = Gtk.Window()
        self.window.set_name("floating-button")
        self.window.set_title("VSCode Widget")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)

        # Configuración adaptativa para X11 y Wayland (v3.3.4 mejorado)
        if self.env['display_server'] == 'wayland':
            # En Wayland: usar DOCK sin padre temporal (más compatible)
            self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
            # En Wayland, usar DOCK sin padre temporal funciona mejor
            # No usar set_transient_for en Wayland para evitar errores
            self.window.set_skip_taskbar_hint(True)
            self.window.set_skip_pager_hint(True)
            self.window.set_accept_focus(True)  # En Wayland necesitamos focus para drag
            self.window.set_property("can-focus", True)
            # Forzar que la ventana sea completamente transparente para eventos
            self.window.set_app_paintable(True)
        else:
            # En X11: usar UTILITY sin padre
            self.window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
            self.window.set_skip_taskbar_hint(True)
            self.window.set_skip_pager_hint(True)
            self.window.set_accept_focus(False)  # No aceptar foco para evitar problemas
            self.window.set_property("can-focus", False)

        # Set window size - botón muy compacto
        self.button_size = 36
        # Forzar tamaño exacto de la ventana
        self.window.set_default_size(self.button_size, self.button_size)
        self.window.set_size_request(self.button_size, self.button_size)
        self.window.set_resizable(False)
        # Configurar geometría fija
        geometry = Gdk.Geometry()
        geometry.min_width = self.button_size
        geometry.max_width = self.button_size
        geometry.min_height = self.button_size
        geometry.max_height = self.button_size
        self.window.set_geometry_hints(None, geometry,
                                       Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE)

        # Position window in bottom right corner by default
        screen = Gdk.Screen.get_default()
        if self.config.get('first_run', True):
            # Primera vez: posicionar en esquina inferior derecha
            # Usar métodos modernos para obtener dimensiones de pantalla
            display = Gdk.Display.get_default()
            monitor = display.get_primary_monitor() or display.get_monitor(0)
            geometry = monitor.get_geometry()
            screen_width = geometry.width
            screen_height = geometry.height
            # Posicionar en el centro de la pantalla para pruebas
            self.config['position_x'] = screen_width // 2 - self.button_size // 2
            self.config['position_y'] = screen_height // 2 - self.button_size // 2
            # v3.3.6: Widget siempre visible por defecto (optimización)
            self.config['always_visible'] = True
            self.config['first_run'] = False
            self.save_config()

        self.window.move(self.config['position_x'], self.config['position_y'])

        # NO usar transparencia - causa problemas de visibilidad
        self.window.set_app_paintable(False)

        # Create button
        self.create_button()

        # Create favorites container
        self.create_favorites_container()

        # Apply CSS
        self.apply_styles()

        # Enable dragging - eventos en la ventana principal
        self.window.connect('button-press-event', self.on_button_press)
        self.window.connect('button-release-event', self.on_button_release)
        self.window.connect('motion-notify-event', self.on_motion)
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)
        
        # CRÍTICO: También habilitar eventos en el botón para capturar clics
        self.button.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)

        # OPTIMIZACIÓN: Eliminar timer periódico - usar eventos bajo demanda
        # El z-order se corregirá solo cuando sea necesario (después de drag/show)
        # timer_id = GLib.timeout_add(5000, self._periodic_zorder_check)
        # self.active_timers.append(timer_id)

        self.window.connect('destroy', self.cleanup)
        self.window.connect('destroy', Gtk.main_quit)

        # Show window - siempre visible para pruebas
        self.window.show_all()
        self.set_window_opacity(1.0)
        self.window_opacity = 1.0
        self.is_nautilus_focused = True

        # Posicionar botones secundarios después de que la ventana esté visible
        # Se hará en el primer fade_in()

        # Forzar la posición guardada después de que la ventana se muestre
        # Esto previene que el window manager reposicione la ventana
        GLib.idle_add(self._restore_saved_position)
        GLib.timeout_add(100, self._restore_saved_position)  # Backup después de 100ms

    def set_window_opacity(self, opacity):
        """Set opacity for main window"""
        self.window_opacity = opacity
        # Suprimir warnings de deprecación temporalmente
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.window.set_opacity(opacity)

    def set_widget_opacity(self, widget, opacity):
        """Set opacity for a widget"""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            widget.set_opacity(opacity)

    def cleanup(self, _widget=None):
        """Limpiar todos los recursos: timers, ventanas, procesos"""
        self.logger.info("Iniciando cleanup de recursos...")

        # 1. Eliminar todos los timers activos
        for timer_id in self.active_timers:
            try:
                if GLib.source_remove(timer_id):
                    self.logger.debug(f"Timer {timer_id} eliminado")
            except Exception as e:
                self.logger.warning(f"Error eliminando timer {timer_id}: {e}")
        self.active_timers.clear()

        # 2. Eliminar timers específicos si existen
        if self.fade_timer:
            try:
                GLib.source_remove(self.fade_timer)
                self.fade_timer = None
            except Exception as e:
                self.logger.warning(f"Error eliminando fade_timer: {e}")

        if self.animation_timer:
            try:
                GLib.source_remove(self.animation_timer)
                self.animation_timer = None
            except Exception as e:
                self.logger.warning(f"Error eliminando animation_timer: {e}")

        if self.focus_timer_id:
            try:
                GLib.source_remove(self.focus_timer_id)
                self.focus_timer_id = None
            except Exception as e:
                self.logger.warning(f"Error eliminando focus_timer_id: {e}")

        if self.dir_timer_id:
            try:
                GLib.source_remove(self.dir_timer_id)
                self.dir_timer_id = None
            except Exception as e:
                self.logger.warning(f"Error eliminando dir_timer_id: {e}")

        # 3. Limpiar cache de subprocess (ahora usa lru_cache - se limpia automáticamente)
        # No es necesario limpiar manualmente - lru_cache lo gestiona automáticamente

        # 4. Destruir ventana de favoritos
        if hasattr(self, 'favorites_window'):
            try:
                self.favorites_window.destroy()
                self.logger.debug("favorites_window destruida")
            except Exception as e:
                self.logger.warning(f"Error destruyendo favorites_window: {e}")

        # 5. Limpiar procesos lanzados (no matar, solo limpiar referencias)
        self.launched_processes.clear()

        self.logger.info("Cleanup completado")

    def setup_logging(self):
        """Setup advanced logging system with diagnostics"""
        log_dir = get_log_dir()

        # Usar el nuevo sistema de logging optimizado
        self.logger = setup_advanced_logging(log_dir)

        # Registrar diagnóstico completo del sistema
        log_system_diagnostics(self.logger)

    def load_config(self):
        """Load configuration from file with validation"""
        default_config = {
            'position_x': 100,
            'position_y': 100,
            'editor_command': 'code',
            'button_color': '#2C2C2C',
            'show_label': False,
            'autostart': False,
            'always_visible': True,  # Widget siempre visible (v3.3.6 - optimización de rendimiento)
            'favorite_folders': [],  # Lista de carpetas favoritas
            'favorite_colors': {}  # Diccionario de colores para carpetas favoritas
        }

        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                self.logger.info(f"Directorio de configuración creado: {config_dir}")

            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Validar configuración cargada
                self.config = self.validate_config(loaded_config, default_config)
                self.logger.info("Configuración cargada exitosamente")
            else:
                self.config = default_config
                self.save_config()
                self.logger.info("Configuración por defecto creada")
                
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            self.config = default_config

    def validate_config(self, loaded_config, default_config):
        """Validate and sanitize loaded configuration"""
        validated_config = default_config.copy()
        
        # Validar tipos de datos
        for key, default_value in default_config.items():
            if key in loaded_config:
                loaded_value = loaded_config[key]
                
                # Validar tipo de dato
                if type(loaded_value) != type(default_value):
                    self.logger.warning(f"Tipo incorrecto para {key}: {type(loaded_value)}. Usando valor por defecto.")
                    continue
                
                # Validaciones específicas por tipo
                if isinstance(default_value, list):
                    # Para listas, verificar que todos los elementos sean strings
                    if all(isinstance(item, str) for item in loaded_value):
                        validated_config[key] = loaded_value
                    else:
                        self.logger.warning(f"Lista inválida para {key}. Usando valor por defecto.")
                elif isinstance(default_value, dict):
                    # Para diccionarios, verificar que claves y valores sean strings
                    if all(isinstance(k, str) and isinstance(v, str) for k, v in loaded_value.items()):
                        validated_config[key] = loaded_value
                    else:
                        self.logger.warning(f"Diccionario inválido para {key}. Usando valor por defecto.")
                elif isinstance(default_value, bool):
                    validated_config[key] = bool(loaded_value)
                elif isinstance(default_value, int):
                    # Para enteros, verificar rango razonable
                    if -10000 <= loaded_value <= 10000:
                        validated_config[key] = loaded_value
                    else:
                        self.logger.warning(f"Valor fuera de rango para {key}: {loaded_value}. Usando valor por defecto.")
                elif isinstance(default_value, str):
                    # Para strings, validar formato de color si es button_color
                    if key == 'button_color':
                        if self.is_valid_color(loaded_value):
                            validated_config[key] = loaded_value
                        else:
                            self.logger.warning(f"Color inválido para {key}: {loaded_value}. Usando valor por defecto.")
                    else:
                        validated_config[key] = loaded_value
                else:
                    validated_config[key] = loaded_value
        
        return validated_config

    def is_valid_color(self, color_str):
        """Validate color string format"""
        if not isinstance(color_str, str):
            return False
        
        # Validar formato hexadecimal
        if color_str.startswith('#') and len(color_str) in [4, 7, 9]:
            try:
                int(color_str[1:], 16)
                return True
            except ValueError:
                return False
        
        # Validar nombres de colores CSS básicos
        basic_colors = ['black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 
                       'gray', 'grey', 'orange', 'purple', 'pink', 'brown']
        return color_str.lower() in basic_colors

    def save_config(self):
        """Save configuration to file"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}", exc_info=True)

    def create_button(self):
        """Create the main button"""
        # Main container - Fixed box en lugar de Overlay
        fixed = Gtk.Fixed()
        fixed.set_app_paintable(True)
        # Forzar tamaño exacto del contenedor - NO permitir expansión
        fixed.set_size_request(self.button_size, self.button_size)
        fixed.set_hexpand(False)
        fixed.set_vexpand(False)
        self.window.add(fixed)

        # Button - posicionado en 0,0 para que esté completamente fijo
        self.button = Gtk.Button()
        self.button.set_size_request(self.button_size, self.button_size)
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        # Eliminar cualquier margen o padding
        self.button.set_margin_top(0)
        self.button.set_margin_bottom(0)
        self.button.set_margin_start(0)
        self.button.set_margin_end(0)
        # NO usar FILL ni expand - mantener tamaño fijo
        self.button.set_halign(Gtk.Align.START)
        self.button.set_valign(Gtk.Align.START)
        self.button.set_hexpand(False)
        self.button.set_vexpand(False)

        # Button content - diseño compacto
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        # Sin márgenes en el contenedor interno
        box.set_margin_top(0)
        box.set_margin_bottom(0)
        box.set_margin_start(0)
        box.set_margin_end(0)

        # Try to load VSCode icon, fallback to SVG or emoji
        icon_loaded = False
        try:
            # Try to load VSCode icon from system with more comprehensive search
            icon_theme = Gtk.IconTheme.get_default()
            vscode_icon_names = [
                'com.visualstudio.code',
                'vscode',
                'visual-studio-code',
                'code',
                'code-binary',
                'visual-studio',
                'com.microsoft.vscode',
                'vscodium',
                'com.vscodium.codium'
            ]

            for icon_name in vscode_icon_names:
                if icon_theme.has_icon(icon_name):
                    try:
                        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
                        icon.set_pixel_size(24)
                        box.pack_start(icon, True, True, 0)
                        icon_loaded = True
                        self.logger.info(f"Icono cargado: {icon_name}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Error cargando icono {icon_name}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"No se pudo cargar icono del sistema: {e}")

        # If icon not found, try custom SVG path with more locations
        if not icon_loaded:
            custom_icon_paths = [
                '/usr/share/pixmaps/vscode.png',
                '/usr/share/icons/hicolor/256x256/apps/code.png',
                '/usr/share/icons/hicolor/48x48/apps/code.png',
                '/usr/share/icons/hicolor/32x32/apps/code.png',
                '/var/lib/snapd/desktop/applications/code_code.desktop',
                '/snap/code/current/meta/gui/com.visualstudio.code.png',
                '/opt/visual-studio-code/resources/app/resources/linux/code.png',
                os.path.expanduser('~/.local/share/icons/vscode.png'),
                os.path.expanduser('~/.local/share/icons/hicolor/256x256/apps/code.png'),
                # Try to use the project's icon.svg if available
                os.path.join(get_executable_dir(), 'icon.svg'),
                os.path.join(get_executable_dir(), 'icon.png')
            ]

            for icon_path in custom_icon_paths:
                if os.path.exists(icon_path):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 24, 24, True)
                        icon = Gtk.Image.new_from_pixbuf(pixbuf)
                        box.pack_start(icon, True, True, 0)
                        icon_loaded = True
                        self.logger.info(f"Icono cargado desde archivo: {icon_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Error cargando {icon_path}: {e}")
                        continue

        # Final fallback: use the lightning emoji as requested
        if not icon_loaded:
            icon_label = Gtk.Label()
            icon_label.set_markup('<span font="20" weight="bold" foreground="white">⚡</span>')
            box.pack_start(icon_label, True, True, 0)

        self.button.add(box)

        # Habilitar eventos de mouse en el botón
        self.button.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)

        self.button.connect('clicked', self.on_button_clicked)

        # Right-click menu y drag con click largo
        self.button.connect('button-press-event', self.on_button_press_event)
        self.button.connect('button-release-event', self.on_button_release_event)
        self.button.connect('motion-notify-event', self.on_button_motion)

        # Añadir botón al Fixed container en posición 0,0
        fixed.put(self.button, 0, 0)

        # Tooltip
        self.update_tooltip()

    def create_favorites_container(self):
        """Crear contenedor unificado para botones favoritos"""
        # Crear ventana para el contenedor de favoritos
        self.favorites_window = Gtk.Window()
        self.favorites_window.set_decorated(False)
        # Usar UTILITY de nuevo pero sin keep_above
        self.favorites_window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.favorites_window.set_skip_taskbar_hint(True)
        self.favorites_window.set_skip_pager_hint(True)
        self.favorites_window.set_accept_focus(False)
        self.favorites_window.set_app_paintable(True)
        self.favorites_window.set_name("favorites-container")
        # Permitir que la ventana pase eventos de mouse a través de áreas transparentes
        self.favorites_window.set_property("can-focus", False)
        # CRÍTICO: Hacer que la ventana NO capture eventos excepto en widgets específicos
        self.favorites_window.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                         Gdk.EventMask.BUTTON_RELEASE_MASK)

        # Tamaño del contenedor - se ajustará dinámicamente
        self.favorites_window.set_default_size(60, 60)
        self.favorites_window.set_resizable(False)

        # Transparencia
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual:
            self.favorites_window.set_visual(visual)

        # Crear layout principal para el contenedor
        self.favorites_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.favorites_box.set_halign(Gtk.Align.CENTER)  # Centrar horizontalmente todo el contenedor
        self.favorites_box.set_valign(Gtk.Align.START)  # Alinear al inicio (arriba) para orden correcto
        self.favorites_box.set_margin_top(4)
        self.favorites_box.set_margin_bottom(4)
        self.favorites_box.set_margin_start(4)
        self.favorites_box.set_margin_end(4)

        self.favorites_window.add(self.favorites_box)

        self.favorites_window.show_all()

        # Inicialmente oculto
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.favorites_window.set_opacity(0.0)

        # Crear botones favoritos y botón de añadir
        self.rebuild_favorites_list()

    def rebuild_favorites_list(self):
        """Reconstruir toda la lista de favoritos en el orden correcto"""
        # Limpiar todos los botones del contenedor de forma segura
        children = self.favorites_box.get_children()
        for child in children:
            self.favorites_box.remove(child)
            child.destroy()

        # Limpiar referencias
        self.favorite_buttons = []
        self.add_button = None

        # Primero: añadir carpetas favoritas (arriba)
        for i, folder_path in enumerate(self.config.get('favorite_folders', [])):
            self.create_favorite_button(folder_path, i)

        # Último: añadir botón + (abajo)
        self.create_add_button_internal()

        # Aplicar estilos y actualizar posiciones DESPUÉS de crear todos los botones
        GLib.idle_add(self._post_rebuild_updates)

    def _post_rebuild_updates(self):
        """Ejecutar actualizaciones después de reconstruir la lista de favoritos"""
        try:
            # Aplicar estilos
            self.apply_styles()
            # Actualizar posiciones
            self.update_favorite_positions()
        except Exception as e:
            self.logger.error(f"Error en _post_rebuild_updates: {e}", exc_info=True)
        return False  # No repetir

    def create_add_button_internal(self):
        """Crear el botón pequeño de añadir (+) en el contenedor de favoritos"""
        # Tamaño del botón - mismo tamaño que los favoritos para consistencia
        btn_size = 24

        # Crear botón con clase CSS
        add_btn = Gtk.Button()
        add_btn.set_name("add-fav-button")
        add_btn.set_size_request(btn_size, btn_size)
        add_btn.set_relief(Gtk.ReliefStyle.NONE)
        add_btn.set_halign(Gtk.Align.CENTER)  # Alineación horizontal centrada
        add_btn.set_valign(Gtk.Align.CENTER)  # Alineación vertical centrada

        # Icono + más pequeño y discreto
        label = Gtk.Label()
        label.set_markup('<span font="10" weight="normal" foreground="white">+</span>')
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        label.set_margin_top(0)
        label.set_margin_bottom(0)
        label.set_margin_start(0)
        label.set_margin_end(0)

        add_btn.add(label)

        add_btn.connect('clicked', self.on_add_folder_clicked)
        add_btn.set_tooltip_text("Añadir carpeta favorita")

        # Añadir al contenedor de favoritos (al final) centrado
        self.favorites_box.pack_start(add_btn, False, False, 0)

        # Guardar referencia
        self.add_button = {
            'button': add_btn,
            'size': btn_size
        }

        # Mostrar el botón
        add_btn.show_all()


    def create_favorite_button(self, folder_path, index):
        """Crear un botón individual de carpeta favorita en el contenedor unificado"""
        # Tamaño del botón - debe ser exactamente igual al del botón +
        btn_size = 24

        # Crear botón con clase CSS única para cada favorito
        fav_btn = Gtk.Button()
        fav_btn.set_name(f"fav-button-{index}")
        fav_btn.set_size_request(btn_size, btn_size)
        fav_btn.set_relief(Gtk.ReliefStyle.NONE)
        fav_btn.set_halign(Gtk.Align.CENTER)  # Alineación horizontal centrada
        fav_btn.set_valign(Gtk.Align.CENTER)  # Alineación vertical centrada

        # Icono de carpeta con inicial centrado perfectamente
        folder_name = os.path.basename(folder_path)
        initial = folder_name[0].upper() if folder_name else "F"

        label = Gtk.Label()
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        label.set_markup(f'<span font="10" weight="bold" foreground="white">{initial}</span>')
        label.set_margin_top(0)
        label.set_margin_bottom(0)
        label.set_margin_start(0)
        label.set_margin_end(0)

        fav_btn.add(label)

        # Conectar eventos
        fav_btn.connect('clicked', lambda b: self.on_favorite_clicked(folder_path))
        fav_btn.connect('button-press-event', lambda w, e: self.on_favorite_right_click(w, e, folder_path))
        fav_btn.set_tooltip_text(f"Abrir: {folder_path}")

        # Añadir al contenedor de favoritos
        self.favorites_box.pack_start(fav_btn, False, False, 0)

        # Guardar referencia
        fav_data = {
            'button': fav_btn,
            'path': folder_path,
            'size': btn_size,
            'index': index
        }
        self.favorite_buttons.append(fav_data)

        # Mostrar el botón
        fav_btn.show_all()


    def update_favorite_positions(self):
        """Actualizar las posiciones de los botones favoritos y el botón +"""
        if not hasattr(self, 'favorites_window'):
            return

        # Calcular tamaño del contenedor basado en número de botones
        num_buttons = len(self.favorite_buttons)

        # Tamaño del contenedor
        btn_size = 24
        spacing = 4
        margin = 8

        # Calcular tamaño del contenedor
        container_width = btn_size + margin * 2
        if num_buttons == 0:
            # Solo el botón + : darle más margen para evitar superposición
            container_height = btn_size + margin * 2
        else:
            # Favoritos + botón +
            container_height = (btn_size + spacing) * (num_buttons + 1) + margin * 2 - spacing

        self.favorites_window.set_default_size(container_width, container_height)

        # Posicionar el contenedor encima del botón principal
        main_x, main_y = self.window.get_position()
        main_center_x = main_x + self.button_size // 2

        # Calcular posición centrada horizontalmente
        container_x = main_center_x - container_width // 2

        # Posicionar encima del botón principal
        # Separación óptima: pegados pero sin superposición
        separation = 8 if num_buttons == 0 else 6  # Más pegados
        container_y = main_y - container_height - separation

        self.favorites_window.move(container_x, container_y)

        # IMPORTANTE: Solo mostrar si la ventana principal está visible
        # Si está oculta (opacidad 0), también ocultar favoritos para evitar bloquear eventos
        if self.window_opacity > 0:
            self.favorites_window.show()
            self.set_widget_opacity(self.favorites_window, self.window_opacity)

            # CRÍTICO: Forzar z-order después de cada actualización para evitar que se pierda
            GLib.idle_add(self._ensure_correct_zorder)
        else:
            # Ocultar completamente para no bloquear eventos del mouse
            self.favorites_window.hide()

    def _ensure_correct_zorder(self):
        """Asegurar que el z-order sea correcto: favoritos abajo, botón principal arriba"""
        try:
            if self.favorites_window.get_window() and self.window.get_window():
                # Primero bajar favoritos
                self.favorites_window.get_window().lower()
                # Luego subir botón principal
                self.window.get_window().raise_()
        except Exception as e:
            self.logger.error(f"Error en _ensure_correct_zorder: {e}", exc_info=True)
        return False  # No repetir

    # OPTIMIZACIÓN: Función eliminada - ya no se usa timer periódico
    # El z-order se corrige bajo demanda llamando a _ensure_correct_zorder()
    # después de eventos que lo requieran (drag, show, etc.)

    def _restore_saved_position(self):
        """Forzar la restauración de la posición guardada en la configuración.
        Esto previene que el window manager reposicione la ventana al mostrarla."""
        try:
            # Verificar que no es la primera ejecución
            if not self.config.get('first_run', True):
                saved_x = self.config.get('position_x', 100)
                saved_y = self.config.get('position_y', 100)

                # Obtener posición actual
                current_x, current_y = self.window.get_position()

                # Solo mover si la posición actual es diferente a la guardada
                # Tolerancia de 5 píxeles para evitar movimientos innecesarios
                if abs(current_x - saved_x) > 5 or abs(current_y - saved_y) > 5:
                    self.window.move(saved_x, saved_y)
                    self.logger.info(f"Posición restaurada a ({saved_x}, {saved_y}) desde ({current_x}, {current_y})")
        except Exception as e:
            self.logger.error(f"Error restaurando posición: {e}")

        return False  # No repetir, solo ejecutar una vez

    def on_add_folder_clicked(self, button):
        """Manejar clic en el botón de añadir carpeta"""
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar carpeta favorita",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder_path = dialog.get_filename()
            if folder_path and folder_path not in self.config.get('favorite_folders', []):
                # Añadir a la configuración
                if 'favorite_folders' not in self.config:
                    self.config['favorite_folders'] = []
                self.config['favorite_folders'].append(folder_path)
                self.save_config()

                # Reconstruir lista completa de favoritos (incluye update_favorite_positions)
                self.rebuild_favorites_list()

                # Si Nautilus está enfocado, mostrar el contenedor de favoritos
                if self.is_nautilus_focused and hasattr(self, 'favorites_window'):
                    self.set_widget_opacity(self.favorites_window, self.window_opacity)

        dialog.destroy()

    def on_favorite_clicked(self, folder_path):
        """Abrir carpeta favorita en VSCode"""
        if os.path.exists(folder_path):
            temp_dir = self.current_directory  # Guardar el directorio actual
            self.current_directory = folder_path  # Temporalmente cambiar
            self.try_open_with_editor()
            self.current_directory = temp_dir  # Restaurar

    def on_favorite_right_click(self, widget, event, folder_path):
        """Mostrar menú contextual para eliminar carpeta favorita"""
        if event.button == 3:  # Clic derecho
            menu = Gtk.Menu()

            # Item para cambiar color
            color_item = Gtk.MenuItem(label="🎨 Cambiar color")
            color_item.connect('activate', lambda x: self.show_color_picker(folder_path))
            menu.append(color_item)

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            # Item para eliminar
            delete_item = Gtk.MenuItem(label="❌ Eliminar de favoritos")
            delete_item.connect('activate', lambda x: self.remove_favorite_folder(folder_path))
            menu.append(delete_item)

            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)
            return True
        return False

    def remove_favorite_folder(self, folder_path):
        """Eliminar carpeta de favoritos"""
        if folder_path in self.config.get('favorite_folders', []):
            self.config['favorite_folders'].remove(folder_path)
            self.save_config()

            # Reconstruir lista completa de favoritos (incluye update_favorite_positions)
            self.rebuild_favorites_list()

    def show_color_picker(self, folder_path):
        """Mostrar diálogo para cambiar color de carpeta favorita"""
        dialog = Gtk.ColorChooserDialog(
            title=f"Color para {os.path.basename(folder_path)}",
            parent=None
        )

        # Establecer color actual
        current_color = self.config.get('favorite_colors', {}).get(folder_path, '#1E1E23')
        color = Gdk.RGBA()
        color.parse(current_color)
        dialog.set_rgba(color)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Guardar nuevo color
            new_color = dialog.get_rgba()
            color_hex = f'#{int(new_color.red*255):02x}{int(new_color.green*255):02x}{int(new_color.blue*255):02x}'
            
            # Actualizar configuración
            if 'favorite_colors' not in self.config:
                self.config['favorite_colors'] = {}
            self.config['favorite_colors'][folder_path] = color_hex
            self.save_config()

            # Aplicar nuevos estilos
            self.apply_styles()

        dialog.destroy()

    def apply_styles(self):
        """Apply modern CSS styles with animations and glassmorphism effects"""
        css_provider = Gtk.CssProvider()

        color = self.config.get('button_color', '#007ACC')

        # Convert hex color to rgba with transparency
        hex_color = color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Generate dynamic CSS for favorite buttons with custom colors
        favorite_css = ""
        for i, fav in enumerate(self.favorite_buttons):
            folder_path = fav['path']
            fav_color = self.config.get('favorite_colors', {}).get(folder_path, '#1E1E23')
            fav_hex = fav_color.lstrip('#')
            fav_r, fav_g, fav_b = tuple(int(fav_hex[i:i+2], 16) for i in (0, 2, 4))
            
            favorite_css += f"""
            /* Botón favorito para {os.path.basename(folder_path)} */
            #fav-button-{i} {{
                border-radius: 12px;
                background: rgba({fav_r}, {fav_g}, {fav_b}, 0.95);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 0;
                margin: 0;
            }}

        #fav-button-{i}:hover {{
            background: rgba({fav_r}, {fav_g}, {fav_b}, 1.0);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        #fav-button-{i}:active {{
            background: rgba({fav_r}, {fav_g}, {fav_b}, 0.85);
        }}
            """

        css = f"""
        /* Ventana del widget principal */
        #floating-button {{
            background-color: rgba(0, 0, 0, 0);
            background: transparent;
        }}

        /* Contenedor de favoritos con fondo personalizable */
        #favorites-container {{
            background: rgba(40, 40, 45, 0.95);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}

        /* Botón principal - simple sin sombras */
        #floating-button button {{
            border-radius: 20px;
            background: rgba({r}, {g}, {b}, 0.95);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0;
            margin: 0;
            min-width: 36px;
            min-height: 36px;
        }}

        #floating-button button * {{
            padding: 0;
            margin: 0;
        }}

        #floating-button button:hover {{
            background: rgba({r}, {g}, {b}, 1.0);
            border: 2px solid rgba(255, 255, 255, 0.35);
        }}

        #floating-button button:active {{
            background: rgba({r}, {g}, {b}, 0.85);
        }}

        /* Botón + de añadir favoritos - simple sin sombras */
        #add-fav-button {{
            border-radius: 12px;
            background: rgba(60, 60, 65, 0.85);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0;
            margin: 0;
            opacity: 0.85;
        }}

        #add-fav-button label {{
            padding: 0;
            margin: 0;
            min-width: 0;
            min-height: 0;
        }}

        #add-fav-button:hover {{
            background: rgba(80, 80, 85, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.25);
            opacity: 1.0;
        }}

        #add-fav-button:active {{
            background: rgba(50, 50, 55, 0.8);
            opacity: 0.9;
        }}

        /* Botones de carpetas favoritas por defecto - sin sombras */
        #fav-button {{
            border-radius: 12px;
            background: rgba(30, 30, 35, 0.95);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0;
            margin: 0;
        }}

        #fav-button label {{
            padding: 0;
            margin: 0;
            min-width: 0;
            min-height: 0;
        }}

        #fav-button:hover {{
            background: rgba(40, 40, 45, 1.0);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        #fav-button:active {{
            background: rgba(25, 25, 30, 0.85);
        }}

        {favorite_css}
        """.encode('utf-8')

        css_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def adjust_color(self, hex_color, percent):
        """Adjust color brightness by percentage"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        r = max(0, min(255, r + int(r * percent / 100)))
        g = max(0, min(255, g + int(g * percent / 100)))
        b = max(0, min(255, b + int(b * percent / 100)))

        return f'#{r:02x}{g:02x}{b:02x}'

    def on_button_press_event(self, widget, event):
        """Handle button press on the main button - for dragging and right-click menu"""
        if event.button == 1:  # Left click
            self.dragging = True
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            x, y = self.window.get_position()
            self.drag_offset_x = event.x_root - x
            self.drag_offset_y = event.y_root - y
            
            # Forzar captura de eventos para máquinas virtuales
            widget.grab_add()
            Gdk.pointer_grab(widget.get_window(), True, 
                            Gdk.EventMask.BUTTON_RELEASE_MASK | 
                            Gdk.EventMask.POINTER_MOTION_MASK,
                            None, None, event.time)
            
            self.logger.debug(f"Inicio arrastre - Posición: ({x}, {y}), Offset: ({self.drag_offset_x}, {self.drag_offset_y})")
            return True  # Capturar el evento para evitar conflictos
        elif event.button == 3:  # Right click
            return self.on_button_right_click(widget, event)
        return False

    def on_button_release_event(self, widget, event):
        """Handle button release on the main button"""
        if event.button == 1 and self.dragging:
            # Liberar captura de eventos
            widget.grab_remove()
            Gdk.pointer_ungrab(event.time)
            
            # Check if it was a drag or a click
            drag_distance = ((event.x_root - self.drag_start_x) ** 2 +
                           (event.y_root - self.drag_start_y) ** 2) ** 0.5

            if drag_distance < 5:  # Less than 5 pixels = click, not drag
                # It's a click, trigger the button action
                self.dragging = False
                self.logger.debug("Clic detectado (no arrastre)")
                return False  # Let the clicked signal handle it
            else:
                # It was a drag
                self.dragging = False
                # Save new position
                x, y = self.window.get_position()
                self.config['position_x'] = x
                self.config['position_y'] = y
                self.save_config()
                self.logger.debug(f"Fin arrastre - Nueva posición: ({x}, {y})")
                return True  # Prevent clicked signal
        return False

    def on_button_motion(self, widget, event):
        """Handle mouse motion on the button for dragging"""
        if self.dragging:
            try:
                x = int(event.x_root - self.drag_offset_x)
                y = int(event.y_root - self.drag_offset_y)

                # Validar coordenadas para evitar errores en máquinas virtuales
                screen = Gdk.Screen.get_default()
                screen_width = screen.get_width()
                screen_height = screen.get_height()
                
                # Limitar coordenadas dentro de la pantalla
                x = max(0, min(x, screen_width - self.button_size))
                y = max(0, min(y, screen_height - self.button_size))

                # Mover ventana principal
                self.window.move(x, y)

                # Actualizar posiciones de favoritos de forma sincronizada
                self._update_favorites_during_drag(x, y)
                
                return True
            except Exception as e:
                self.logger.error(f"Error en arrastre: {e}")
                self.dragging = False
                widget.grab_remove()
                Gdk.pointer_ungrab(Gdk.CURRENT_TIME)
        return False

    def _update_favorites_during_drag(self, main_x, main_y):
        """Actualizar posición de favoritos durante el drag de forma optimizada"""
        if not hasattr(self, 'favorites_window') or not self.favorites_window.get_visible():
            return

        # Calcular nueva posición de favoritos basada en la posición del botón principal
        num_buttons = len(self.favorite_buttons)
        btn_size = 24
        spacing = 4
        margin = 8

        container_width = btn_size + margin * 2
        if num_buttons == 0:
            container_height = btn_size + margin * 2
        else:
            container_height = (btn_size + spacing) * (num_buttons + 1) + margin * 2 - spacing

        main_center_x = main_x + self.button_size // 2
        container_x = main_center_x - container_width // 2

        separation = 8 if num_buttons == 0 else 6
        container_y = main_y - container_height - separation

        # Mover ventana de favoritos de forma sincronizada
        self.favorites_window.move(container_x, container_y)

    # OPTIMIZACIÓN: Manejadores de drag simplificados - removido código duplicado
    # Los eventos de la ventana principal ya no son necesarios porque
    # los eventos del botón manejan todo correctamente

    def on_button_press(self, _widget, _event):
        """Backup handler - normalmente no se usa"""
        return False  # Dejar que el manejador del botón lo procese

    def on_button_release(self, _widget, _event):
        """Backup handler - normalmente no se usa"""
        return False  # Dejar que el manejador del botón lo procese

    def on_motion(self, _widget, _event):
        """Backup handler - normalmente no se usa"""
        return False  # Dejar que el manejador del botón lo procese



    def _adjust_check_intervals(self, nautilus_focused):
        """Función legacy - Ya no se usan timers de detección continua"""
        # v3.3.7: Widget siempre visible - sin timers activos
        # Esta función se mantiene para compatibilidad pero no hace nada
        pass

    def fade_in(self):
        """Smoothly fade in the button with animations"""
        if self.fade_timer:
            GLib.source_remove(self.fade_timer)

        # Actualizar posiciones de botones secundarios antes de mostrar
        self.update_favorite_positions()

        # Animación suave de fade in
        self.animate_fade_in()

    def fade_out(self):
        """Smoothly fade out the button with animations"""
        if self.fade_timer:
            GLib.source_remove(self.fade_timer)

        # Animación suave de fade out
        self.animate_fade_out()

    def animate_fade_in(self):
        """Animate fade in with smooth transitions"""
        if self.window_opacity >= 1.0:
            return

        self.window_opacity = min(1.0, self.window_opacity + 0.1)
        self.set_window_opacity(self.window_opacity)

        if self.window_opacity < 1.0:
            self.fade_timer = GLib.timeout_add(20, self.animate_fade_in)
        else:
            # Una vez que el botón principal está visible, animar los favoritos
            self.animate_favorites_expand()

    def animate_fade_out(self):
        """Animate fade out with smooth transitions"""
        if self.window_opacity <= 0.0:
            return

        self.window_opacity = max(0.0, self.window_opacity - 0.1)
        self.set_window_opacity(self.window_opacity)

        if self.window_opacity > 0.0:
            self.fade_timer = GLib.timeout_add(20, self.animate_fade_out)
        else:
            self.favorite_buttons_visible = False
            self.expand_animation_progress = 0.0
            # CRÍTICO: Ocultar ventana de favoritos para no bloquear eventos
            if hasattr(self, 'favorites_window'):
                self.favorites_window.hide()


    def on_button_right_click(self, widget, event):
        """Show context menu on right click"""
        if event.button == 3:  # Right click
            menu = Gtk.Menu()

            # Settings item
            settings_item = Gtk.MenuItem(label="⚙️ Configuración")
            settings_item.connect('activate', self.show_settings)
            menu.append(settings_item)

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            # Quit item
            quit_item = Gtk.MenuItem(label="❌ Salir")
            quit_item.connect('activate', lambda x: Gtk.main_quit())
            menu.append(quit_item)

            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)
            return True

    def on_button_clicked(self, button):
        """Handle button click to open VSCode - detección bajo demanda en thread separado"""
        # Mostrar indicador visual (cambiar opacidad ligeramente)
        original_opacity = self.window_opacity
        self.set_window_opacity(0.7)

        # Ejecutar detección de directorio en thread separado para no bloquear UI
        def detect_and_open():
            try:
                # Thread-safe: usar lock para proteger current_directory
                with self.directory_lock:
                    detected_dir = self.get_nautilus_directory_multiple_methods()

                    # Si no se detectó directorio, usar alternativas inteligentes
                    if not detected_dir or not os.path.exists(detected_dir):
                        detected_dir = self.get_directory_from_fallback()

                    self.current_directory = detected_dir

                # Actualizar UI en el thread principal
                GLib.idle_add(self._open_editor_callback, original_opacity)

            except Exception as e:
                self.logger.error(f"Error en detección de directorio: {e}", exc_info=True)
                GLib.idle_add(self._show_error_callback, str(e), original_opacity)

        # Iniciar thread de detección
        thread = threading.Thread(target=detect_and_open, daemon=True)
        thread.start()

    def _open_editor_callback(self, original_opacity):
        """Callback ejecutado en UI thread después de detectar directorio"""
        # Restaurar opacidad
        self.set_window_opacity(original_opacity)

        if self.current_directory and os.path.exists(self.current_directory):
            success = self.try_open_with_editor()
            if not success:
                # If configured editor fails, try common VSCode commands
                success = self.try_open_with_common_editors()

            if not success:
                self.show_error_dialog(
                    "Editor no encontrado",
                    "No se pudo encontrar ningún editor compatible.\n"
                    "Instala VSCode o configura un editor válido en configuración."
                )
        else:
            self.show_error_dialog(
                "No se detectó carpeta",
                "No se pudo detectar ninguna carpeta válida.\n"
                "Abre una ventana de Nautilus o usa la configuración para establecer una carpeta por defecto."
            )
        return False  # No repetir el callback

    def _show_error_callback(self, error_message, original_opacity):
        """Callback para mostrar errores en UI thread"""
        # Restaurar opacidad
        self.set_window_opacity(original_opacity)

        # Mostrar error
        self.show_error_dialog(
            "Error de detección",
            f"Ocurrió un error al detectar el directorio:\n{error_message}"
        )
        return False  # No repetir el callback

    def try_open_with_editor(self):
        """Try to open with configured editor (v3.3.1 con validación de seguridad mejorada)"""
        start_time = time.time()
        try:
            editor_cmd = self.config.get('editor_command', 'code')
            self.logger.debug(f"Intentando abrir editor: {editor_cmd} -> {self.current_directory}")

            # Validar comando de editor (v3.3.1)
            validated_cmd = validate_editor_command(editor_cmd)
            if not validated_cmd:
                self.logger.warning(f"Comando de editor inválido o no encontrado: {editor_cmd}")
                return False

            # Validar directorio (v3.3.1)
            validated_dir = validate_directory(self.current_directory)
            if not validated_dir:
                self.logger.warning(f"Directorio inválido o inaccesible: {self.current_directory}")
                return False

            # Create the subprocess with proper settings to avoid terminal popup
            process = subprocess.Popen(
                [validated_cmd, validated_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )

            # Guardar referencia al proceso para posible cleanup
            self.launched_processes.append({
                'pid': process.pid,
                'cmd': validated_cmd,
                'time': time.time()
            })

            execution_time = time.time() - start_time
            self.logger.info(f"Editor abierto exitosamente: {validated_cmd} -> {validated_dir} (tiempo: {execution_time:.2f}s, PID: {process.pid})")
            return True

        except FileNotFoundError:
            self.logger.error(f"Comando no encontrado: {editor_cmd}")
            return False
        except PermissionError:
            self.logger.error(f"Sin permisos para ejecutar: {editor_cmd}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout al abrir editor: {editor_cmd}")
            return False
        except Exception as e:
            self.logger.error(f"Error al abrir editor: {e}", exc_info=True)
            return False
    
    def try_open_with_common_editors(self):
        """Try to open with common VSCode installations"""
        # Lista de comandos comunes para VSCode
        vscode_commands = [
            'code',
            'code-insiders', 
            'codium',
            'vscodium',
            '/usr/bin/code',
            '/usr/local/bin/code',
            '/snap/bin/code',
            '/var/lib/flatpak/app/com.visualstudio.code/current/active/export/bin/com.visualstudio.code',
            '/opt/visual-studio-code/bin/code',
            os.path.expanduser('~/.local/bin/code')
        ]
        
        for cmd in vscode_commands:
            try:
                # Check if command exists
                if cmd.startswith('/'):
                    if not os.path.isfile(cmd) or not os.access(cmd, os.X_OK):
                        continue
                else:
                    # Check if command is in PATH
                    check_cmd = subprocess.run(
                        ['which', cmd],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if check_cmd.returncode != 0:
                        continue
                
                # Try to open
                process = subprocess.Popen(
                    [cmd, self.current_directory],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )

                # Guardar referencia al proceso para posible cleanup
                self.launched_processes.append({
                    'pid': process.pid,
                    'cmd': cmd,
                    'time': time.time()
                })

                self.logger.info(f"Abriendo {self.current_directory} con {cmd} (PID: {process.pid})")
                # Update config with working command
                self.config['editor_command'] = cmd
                self.save_config()
                return True

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout al verificar comando: {cmd}")
                continue
            except (FileNotFoundError, PermissionError, OSError):
                continue
            except Exception as _e:
                continue
        
        return False

    def update_current_directory(self):
        """Función legacy - Ya no se usa para detección continua"""
        # v3.3.6: Detección bajo demanda - esta función ya no se usa
        return True  # Mantener para compatibilidad

    def get_nautilus_directory_multiple_methods(self):
        """Try multiple methods to get the current Nautilus directory with improved logging"""
        start_time = time.time()
        methods = [
            ("DBus", self.get_directory_from_dbus),  # Más confiable para Nautilus moderno
            ("Active Window", self.get_directory_from_active_nautilus_window),
            ("Fallback", self.get_directory_from_fallback)
        ]

        for method_name, method in methods:
            try:
                self.logger.debug(f"Intentando método de detección: {method_name}")
                directory = method()
                if directory and os.path.exists(directory):
                    execution_time = time.time() - start_time
                    self.logger.info(f"Directorio detectado con {method_name}: {directory} (tiempo: {execution_time:.2f}s)")
                    return directory
            except Exception as e:
                self.logger.debug(f"Método {method_name} falló: {e}")
                continue

        execution_time = time.time() - start_time
        self.logger.warning(f"No se pudo detectar directorio con ningún método (tiempo: {execution_time:.2f}s)")
        return None

    def get_directory_from_dbus(self):
        """Get directory from Nautilus via DBus - most reliable method"""
        try:
            # Get active Nautilus window ID first
            result = subprocess.run(
                ['xdotool', 'search', '--class', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0 or not result.stdout.strip():
                return None

            # Get focused window
            focused_result = subprocess.run(
                ['xdotool', 'getwindowfocus'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if focused_result.returncode != 0:
                return None

            focused_id = focused_result.stdout.strip()
            window_ids = result.stdout.strip().split('\n')

            # Check if focused window is Nautilus
            if focused_id not in window_ids:
                return None

            # Use gdbus to get current location from Nautilus
            dbus_result = subprocess.run(
                ['gdbus', 'call', '--session',
                 '--dest', 'org.gnome.Nautilus',
                 '--object-path', '/org/gnome/Nautilus/window/1',
                 '--method', 'org.freedesktop.DBus.Properties.Get',
                 'org.gnome.Nautilus.Window', 'location'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if dbus_result.returncode == 0 and dbus_result.stdout:
                # Parse the DBus output
                output = dbus_result.stdout.strip()
                # Format: (<'file:///path/to/directory'>,)
                if 'file://' in output:
                    from urllib.parse import unquote
                    import re
                    match = re.search(r"'(file://[^']+)'", output)
                    if match:
                        uri = match.group(1)
                        path = unquote(uri.replace('file://', ''))
                        if os.path.exists(path) and os.path.isdir(path):
                            return path

        except Exception:
            pass

        return None

    def get_directory_from_active_nautilus_window(self):
        """Get directory from the currently active/focused Nautilus window"""
        try:
            # Get the currently active window
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                active_window_id = result.stdout.strip()
                
                # Get the window title to check if it's Nautilus
                title_result = subprocess.run(
                    ['xdotool', 'getwindowname', active_window_id],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if title_result.returncode == 0:
                    title = title_result.stdout.strip()
                    # Check if this looks like a Nautilus window
                    is_nautilus = (
                        'nautilus' in title.lower() or
                        title.startswith('/') or
                        any(folder in title.lower() for folder in ['documents', 'documentos', 'downloads', 'descargas', 'pictures', 'imágenes', 'music', 'música', 'videos', 'vídeos', 'desktop', 'escritorio']) or
                        len(title) > 3 and title not in ['✳ Carpeta problema']  # Exclude our own window titles
                    )

                if is_nautilus:
                    # Try to get directory from title
                    directory = self.extract_directory_from_title(title)
                    if directory:
                        return directory
                    
                    # If title doesn't have path, try to get it from window properties
                    directory = self.get_directory_from_window_properties(active_window_id)
                    if directory:
                        return directory
            
        except Exception:
            pass
        
        return None
    
    
    def get_directory_from_window_properties(self, window_id):
        """Try to get directory from window properties"""
        try:
            # Try to get window properties that might contain the path
            prop_result = subprocess.run(
                ['xprop', '-id', window_id, 'WM_NAME', '_NET_WM_NAME'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if prop_result.returncode == 0:
                output = prop_result.stdout
                
                # Look for file paths in the properties
                import re
                paths = re.findall(r'["\']([^"\']*file://[^"\']*)["\']', output)
                for path in paths:
                    if 'file://' in path:
                        from urllib.parse import unquote
                        clean_path = unquote(path.replace('file://', ''))
                        if os.path.exists(clean_path) and os.path.isdir(clean_path):
                            return clean_path
                
                # Look for direct paths
                paths = re.findall(r'["\']([^"\']*(?:/[^/"\'\s]+)+)["\']', output)
                for path in paths:
                    if os.path.exists(path) and os.path.isdir(path):
                        return path
            
        except Exception:
            pass
        
        return None
    
    
    def get_directory_from_fallback(self):
        """Fallback method - use smart defaults"""
        try:
            # Try current working directory first
            cwd = os.getcwd()
            if os.path.exists(cwd) and os.path.isdir(cwd):
                return cwd
            
            # Try common directories
            home = os.path.expanduser('~')
            common_dirs = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Escritorio'), 
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Documentos'),
                home
            ]
            
            for directory in common_dirs:
                if os.path.exists(directory) and os.path.isdir(directory):
                    return directory

        except Exception:
            pass
        
        return None

    def extract_directory_from_title(self, title):
        """Extract directory path from window title with improved logic"""
        if not title:
            return None

        # Clean up the title
        original_title = title
        title = title.strip()

        # Remove common prefixes and special characters
        prefixes_to_remove = ['Files', 'Archivos', 'File Manager', 'Gestor de archivos']
        for prefix in prefixes_to_remove:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                if title.startswith('-'):
                    title = title[1:].strip()

        # Remove special characters like ✳ that Nautilus sometimes adds
        title = title.lstrip('✳ ').strip()

        # If it starts with /, it's likely a full path
        if title.startswith('/'):
            if os.path.exists(title):
                return title
        
        # Try to find path patterns in the original title
        import re
        path_pattern = r'(/[^\s]+(?:/[^\s]*)*?)'
        matches = re.findall(path_pattern, original_title)
        for match in matches:
            if os.path.exists(match):
                return match

        # Handle common folder names
        if title and title != '':
            home = os.path.expanduser('~')
            
            # Direct folder name mapping
            folder_mapping = {
                'Documents': 'Documents', 'Documentos': 'Documents',
                'Downloads': 'Downloads', 'Descargas': 'Downloads',
                'Pictures': 'Pictures', 'Imágenes': 'Pictures',
                'Music': 'Music', 'Música': 'Music',
                'Videos': 'Videos', 'Vídeos': 'Videos',
                'Desktop': 'Desktop', 'Escritorio': 'Desktop',
                'Public': 'Public', 'Público': 'Public',
                'Templates': 'Templates', 'Plantillas': 'Templates'
            }
            
            # Special case for home folder
            if title.lower() in ['carpeta personal', 'home', 'personal folder']:
                return home
            
            # Check for exact matches
            for display_name, folder_name in folder_mapping.items():
                if title.lower() == display_name.lower():
                    path = os.path.join(home, folder_name)
                    if os.path.exists(path):
                        return path
            
            # Check for partial matches
            for display_name, folder_name in folder_mapping.items():
                if display_name.lower() in title.lower():
                    path = os.path.join(home, folder_name)
                    if os.path.exists(path):
                        return path

            # Try as subdirectory of home
            if '/' not in title:  # Only if it's a simple name
                path = os.path.join(home, title)
                if os.path.exists(path):
                    return path
            
            # Enhanced search for folder names
            if '/' not in title and title not in ['org.gnome.Nautilus', 'Nautilus']:
                found_path = self.search_folder_by_name(title)
                if found_path:
                    return found_path

        return None
    
    def search_folder_by_name(self, folder_name):
        """Search for a folder by name in common locations"""
        search_locations = [
            os.path.expanduser('~'),
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Documentos'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Escritorio'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Descargas')
        ]
        
        # First try direct subdirectories
        for base_dir in search_locations:
            if os.path.exists(base_dir):
                try:
                    for item in os.listdir(base_dir):
                        if item.lower() == folder_name.lower():
                            full_path = os.path.join(base_dir, item)
                            if os.path.isdir(full_path):
                                return full_path
                except PermissionError:
                    continue
        
        # Then try deeper search (max 2 levels)
        for base_dir in search_locations[:3]:  # Only search in home, Documents, Documentos
            if os.path.exists(base_dir):
                try:
                    found = self.recursive_folder_search(base_dir, folder_name, max_depth=2)
                    if found:
                        return found
                except Exception:
                    continue
        
        return None
    
    def recursive_folder_search(self, base_dir, target_name, max_depth=2, current_depth=0, start_time=None):
        """Recursively search for a folder by name with timeout and better exclusions"""
        # Iniciar timer en la primera llamada
        if start_time is None:
            start_time = time.time()

        # Timeout de 2 segundos para evitar bloqueos
        if time.time() - start_time > 2.0:
            self.logger.warning("Búsqueda recursiva timeout después de 2 segundos")
            return None

        if current_depth >= max_depth:
            return None

        # Directorios a excluir (expandida para mejor rendimiento)
        excluded_dirs = {
            'node_modules', '__pycache__', '.git', '.svn', '.hg',
            '.cache', '.config', '.local', '.npm', '.cargo', '.rustup',
            'venv', 'env', '.venv', '.env', 'virtualenv',
            'site-packages', 'dist', 'build', '.tox',
            'snap', 'flatpak', '.wine', '.steam',
            '.mozilla', '.thunderbird', '.var'
        }

        try:
            # Usar scandir() en lugar de listdir() para mejor rendimiento
            with os.scandir(base_dir) as entries:
                for entry in entries:
                    # Verificar timeout en cada iteración
                    if time.time() - start_time > 2.0:
                        return None

                    try:
                        # Saltar archivos, solo procesar directorios
                        if not entry.is_dir(follow_symlinks=False):
                            continue

                        # Saltar directorios ocultos y excluidos
                        if entry.name.startswith('.') or entry.name in excluded_dirs:
                            continue

                        # Check if this item matches our target
                        if entry.name.lower() == target_name.lower():
                            return entry.path

                        # Recurse into subdirectories
                        if current_depth < max_depth - 1:
                            result = self.recursive_folder_search(
                                entry.path, target_name, max_depth,
                                current_depth + 1, start_time
                            )
                            if result:
                                return result

                    except (PermissionError, OSError):
                        # Saltar directorios sin permisos o con errores
                        continue

        except (PermissionError, OSError) as e:
            self.logger.debug(f"Error accediendo a {base_dir}: {e}")

        return None

    def update_tooltip(self):
        """Update button tooltip with current directory"""
        if self.current_directory:
            self.button.set_tooltip_text(f"Abrir en {self.config['editor_command']}:\n{self.current_directory}")
        else:
            self.button.set_tooltip_text("Esperando carpeta de Nautilus...")

    def show_settings(self, widget=None):
        """Show settings dialog"""
        SettingsDialog(self)

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class SettingsDialog:
    def __init__(self, parent_app):
        self.app = parent_app

        self.dialog = Gtk.Dialog(
            title="Configuración - VSCode Widget",
            parent=None,
            flags=0
        )
        self.dialog.set_default_size(400, 300)
        self.dialog.set_border_width(10)

        # Apply blur effect to settings dialog
        self.apply_dialog_styles()

        # Add buttons
        self.dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Guardar", Gtk.ResponseType.OK)

        # Content area
        box = self.dialog.get_content_area()
        box.set_spacing(10)

        # Title
        title = Gtk.Label()
        title.set_markup('<span font="14" weight="bold">⚙️ Configuración</span>')
        box.pack_start(title, False, False, 10)

        # Editor command
        editor_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        editor_label = Gtk.Label(label="Comando del editor:")
        editor_label.set_width_chars(20)
        editor_label.set_xalign(0)
        self.editor_entry = Gtk.Entry()
        self.editor_entry.set_text(self.app.config.get('editor_command', 'code'))
        self.editor_entry.set_placeholder_text("code, /usr/bin/code, etc.")

        # Browse button
        browse_button = Gtk.Button(label="📁")
        browse_button.set_tooltip_text("Seleccionar ejecutable")
        browse_button.connect('clicked', self.on_browse_editor)

        editor_box.pack_start(editor_label, False, False, 0)
        editor_box.pack_start(self.editor_entry, True, True, 0)
        editor_box.pack_start(browse_button, False, False, 0)
        box.pack_start(editor_box, False, False, 0)

        # Info label
        info_label = Gtk.Label()
        info_label.set_markup('<span font="8" style="italic">💡 Usa "code" o la ruta completa como "/usr/bin/code"</span>')
        info_label.set_xalign(0)
        info_label.set_margin_start(20)
        box.pack_start(info_label, False, False, 0)

        # Button color
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        color_label = Gtk.Label(label="Color del botón:")
        color_label.set_width_chars(20)
        color_label.set_xalign(0)
        self.color_button = Gtk.ColorButton()
        color = Gdk.RGBA()
        color.parse(self.app.config['button_color'])
        self.color_button.set_rgba(color)
        color_box.pack_start(color_label, False, False, 0)
        color_box.pack_start(self.color_button, False, False, 0)
        box.pack_start(color_box, False, False, 0)

        # Show label
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label_label = Gtk.Label(label="Mostrar etiqueta:")
        label_label.set_width_chars(20)
        label_label.set_xalign(0)
        self.show_label_switch = Gtk.Switch()
        self.show_label_switch.set_active(self.app.config['show_label'])
        label_box.pack_start(label_label, False, False, 0)
        label_box.pack_start(self.show_label_switch, False, False, 0)
        box.pack_start(label_box, False, False, 0)

        # Autostart option
        autostart_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        autostart_label = Gtk.Label(label="Iniciar con el sistema:")
        autostart_label.set_width_chars(20)
        autostart_label.set_xalign(0)
        self.autostart_switch = Gtk.Switch()
        # Verificar el estado real del archivo de autostart
        actual_autostart_state = self.check_autostart_enabled()
        self.autostart_switch.set_active(actual_autostart_state)
        # Actualizar el config con el estado real
        self.app.config['autostart'] = actual_autostart_state
        autostart_box.pack_start(autostart_label, False, False, 0)
        autostart_box.pack_start(self.autostart_switch, False, False, 0)
        box.pack_start(autostart_box, False, False, 0)

        # Autostart info
        autostart_info = Gtk.Label()
        autostart_info.set_markup('<span font="8" style="italic">💡 El botón aparecerá automáticamente al iniciar sesión</span>')
        autostart_info.set_xalign(0)
        autostart_info.set_margin_start(20)
        box.pack_start(autostart_info, False, False, 0)

        # Info
        info = Gtk.Label()
        info.set_markup(
            '<span font="9" style="italic">💡 Puedes arrastrar el botón flotante\n'
            'para moverlo a cualquier posición</span>'
        )
        info.set_margin_top(20)
        box.pack_start(info, False, False, 0)

        # Current directory info
        if self.app.current_directory:
            dir_info = Gtk.Label()
            dir_info.set_markup(f'<span font="9">📁 Carpeta actual: {self.app.current_directory}</span>')
            dir_info.set_line_wrap(True)
            dir_info.set_max_width_chars(50)
            box.pack_start(dir_info, False, False, 0)

        # Credits footer
        credits_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        credits_box.set_margin_top(20)

        # Version label
        version_label = Gtk.Label()
        version_label.set_markup(f'<span font="7" foreground="#666666">release: {VERSION}</span>')
        version_label.set_xalign(0.5)
        credits_box.pack_start(version_label, False, False, 0)

        credits_label = Gtk.Label()
        credits_label.set_markup('<span font="7" foreground="#888888">Realizado por Konstantin WDK</span>')
        credits_label.set_xalign(0.5)
        credits_box.pack_start(credits_label, False, False, 0)

        # Clickable link
        web_button = Gtk.LinkButton.new_with_label("https://webdesignerk.com", "webdesignerk.com")
        web_button.set_relief(Gtk.ReliefStyle.NONE)
        web_button.set_halign(Gtk.Align.CENTER)
        credits_box.pack_start(web_button, False, False, 0)

        box.pack_end(credits_box, False, False, 0)

        self.dialog.show_all()

        response = self.dialog.run()

        if response == Gtk.ResponseType.OK:
            self.save_settings()

        self.dialog.destroy()

    def apply_dialog_styles(self):
        """Apply modern styles with blur to dialog"""
        css_provider = Gtk.CssProvider()

        css = """
        dialog {
            background: rgba(50, 50, 55, 0.98);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }

        dialog headerbar {
            background: rgba(60, 60, 65, 0.98);
            border-radius: 12px 12px 0 0;
            color: white;
        }

        dialog headerbar label {
            color: white;
        }

        dialog box {
            background: transparent;
        }

        dialog entry {
            border-radius: 6px;
            padding: 8px;
            background: rgba(70, 70, 75, 0.9);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        dialog entry:focus {
            border: 1px solid rgba(100, 150, 255, 0.6);
            box-shadow: 0 0 0 3px rgba(100, 150, 255, 0.2);
            background: rgba(80, 80, 85, 0.95);
        }

        dialog button {
            border-radius: 6px;
            padding: 8px 16px;
            background: rgba(70, 70, 75, 0.9);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        dialog button:hover {
            background: rgba(90, 90, 95, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        dialog label {
            color: #ffffff;
        }

        dialog switch {
            background: rgba(70, 70, 75, 0.9);
        }

        dialog switch:checked {
            background: rgba(100, 150, 255, 0.8);
        }
        """.encode('utf-8')

        css_provider.load_from_data(css)

        style_context = self.dialog.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def save_settings(self):
        """Save settings and apply changes"""
        # Update config
        self.app.config['editor_command'] = self.editor_entry.get_text()

        rgba = self.color_button.get_rgba()
        self.app.config['button_color'] = f'#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}'

        self.app.config['show_label'] = self.show_label_switch.get_active()

        # Handle autostart
        autostart_enabled = self.autostart_switch.get_active()
        self.app.config['autostart'] = autostart_enabled

        if autostart_enabled:
            self.enable_autostart()
        else:
            self.disable_autostart()

        # Save to file
        self.app.save_config()

        # Restart app to apply changes
        self.show_restart_dialog()

    def check_autostart_enabled(self):
        """Check if autostart is enabled by verifying the .desktop file exists"""
        try:
            desktop_file = get_autostart_file()
            return os.path.exists(desktop_file)
        except Exception as e:
            self.app.logger.error(f"Error verificando autostart: {e}", exc_info=True)
            return False

    def enable_autostart(self):
        """Enable autostart by creating .desktop file"""
        try:
            desktop_file = get_autostart_file()

            # Determinar el comando de ejecución según el modo
            if self.app.is_portable:
                # Modo portable: usar el ejecutable
                exec_path = sys.executable
                exec_cmd = f'"{exec_path}"'
            else:
                # Modo instalado: usar python3 + script
                script_path = os.path.abspath(__file__)
                exec_cmd = f'python3 "{script_path}"'

            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Nautilus VSCode Widget
Comment=Floating button to open folders in VSCode from Nautilus
Exec={exec_cmd}
Icon=com.visualstudio.code
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
Categories=Utility;Development;
StartupNotify=false
"""

            with open(desktop_file, 'w') as f:
                f.write(desktop_content)

            # Make it executable
            os.chmod(desktop_file, 0o755)

            self.app.logger.info(f"Autostart habilitado: {desktop_file}")
            if self.app.is_portable:
                self.app.logger.info(f"Modo portable: ejecutable en {exec_path}")

        except Exception as e:
            self.app.logger.error(f"Error habilitando autostart: {e}", exc_info=True)

    def disable_autostart(self):
        """Disable autostart by removing .desktop file"""
        try:
            desktop_file = get_autostart_file()
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
                self.app.logger.info("Autostart deshabilitado")
        except Exception as e:
            self.app.logger.error(f"Error deshabilitando autostart: {e}", exc_info=True)

    def on_browse_editor(self, button):
        """Open file chooser to select editor executable"""
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar editor",
            parent=self.dialog,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Add filter for executables
        filter_exec = Gtk.FileFilter()
        filter_exec.set_name("Ejecutables")
        filter_exec.add_mime_type("application/x-executable")
        filter_exec.add_pattern("*")
        dialog.add_filter(filter_exec)

        # Set initial folder to /usr/bin
        dialog.set_current_folder("/usr/bin")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_file = dialog.get_filename()
            self.editor_entry.set_text(selected_file)

        dialog.destroy()

    def show_restart_dialog(self):
        """Show restart confirmation"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Configuración guardada"
        )
        dialog.format_secondary_text(
            "Reinicia la aplicación para aplicar los cambios.\n"
            "Puedes hacerlo desde el menú del botón flotante."
        )
        dialog.run()
        dialog.destroy()


def main():
    app = FloatingButtonApp()
    Gtk.main()


if __name__ == '__main__':
    main()
