#!/usr/bin/env python3
"""
Floating Button Application
Una aplicación con botón flotante que detecta la carpeta activa en Nautilus
y permite abrirla en VSCode
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import os
import re
import json


class FloatingButtonApp:
    def __init__(self):
        self.config_file = os.path.expanduser('~/.config/nautilus-vscode-opener/config.json')
        self.load_config()

        # Initialize variables FIRST
        self.current_directory = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Create floating button window
        self.window = Gtk.Window()
        self.window.set_title("VSCode Opener")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_accept_focus(False)

        # Set window size - botón más grande y bonito
        self.button_size = 70
        self.window.set_default_size(self.button_size, self.button_size)
        self.window.set_resizable(False)

        # Position window in bottom right corner by default
        screen = Gdk.Screen.get_default()
        if self.config.get('first_run', True):
            # Primera vez: posicionar en esquina inferior derecha
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            self.config['position_x'] = screen_width - self.button_size - 20
            self.config['position_y'] = screen_height - self.button_size - 80
            self.config['first_run'] = False
            self.save_config()

        self.window.move(self.config['position_x'], self.config['position_y'])

        # Make window transparent
        visual = screen.get_rgba_visual()
        if visual:
            self.window.set_visual(visual)

        self.window.set_app_paintable(True)

        # Create button
        self.create_button()

        # Apply CSS
        self.apply_styles()

        # Enable dragging
        self.window.connect('button-press-event', self.on_button_press)
        self.window.connect('button-release-event', self.on_button_release)
        self.window.connect('motion-notify-event', self.on_motion)
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)

        # Start monitoring Nautilus windows
        GLib.timeout_add(500, self.update_current_directory)

        self.window.connect('destroy', Gtk.main_quit)

        # Always show button initially - let the timer handle hiding/showing
        print("Mostrando botón flotante...")
        self.window.show_all()
        
        # Check if Nautilus is running for initial state
        check_nautilus = subprocess.run(
            ['pgrep', '-x', 'nautilus'],
            capture_output=True,
            text=True
        )
        
        if check_nautilus.returncode == 0:
            print("Nautilus detectado en inicio")
        else:
            print("Nautilus no detectado en inicio - esperando...")

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'position_x': 100,
            'position_y': 100,
            'editor_command': 'code',
            'button_color': '#007ACC',
            'show_label': True
        }

        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config

    def save_config(self):
        """Save configuration to file"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_button(self):
        """Create the main button"""
        # Main container
        overlay = Gtk.Overlay()
        self.window.add(overlay)

        # Button
        self.button = Gtk.Button()
        self.button.set_size_request(self.button_size, self.button_size)
        self.button.set_relief(Gtk.ReliefStyle.NONE)

        # Button content - diseño más bonito
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        # Icon más grande y llamativo
        icon_label = Gtk.Label()
        icon_label.set_markup('<span font="28" weight="bold">📁</span>')
        box.pack_start(icon_label, False, False, 0)

        # Label con mejor estilo
        if self.config.get('show_label', True):
            label = Gtk.Label()
            label.set_markup('<span font="9" weight="bold">VS Code</span>')
            box.pack_start(label, False, False, 0)

        self.button.add(box)
        self.button.connect('clicked', self.on_button_clicked)

        # Right-click menu
        self.button.connect('button-press-event', self.on_button_right_click)

        overlay.add(self.button)

        # Tooltip
        self.update_tooltip()

    def apply_styles(self):
        """Apply CSS styles to the window and button"""
        css_provider = Gtk.CssProvider()

        color = self.config.get('button_color', '#007ACC')

        css = f"""
        window {{
            background-color: transparent;
        }}

        button {{
            border-radius: 35px;
            background: linear-gradient(145deg, {color} 0%, {self.adjust_color(color, -15)} 100%);
            color: white;
            border: 3px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: bold;
        }}

        button:hover {{
            background: linear-gradient(145deg, {self.adjust_color(color, 15)} 0%, {color} 100%);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
            border: 3px solid rgba(255, 255, 255, 0.5);
        }}

        button:active {{
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3), inset 0 1px 3px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, {self.adjust_color(color, -10)} 0%, {self.adjust_color(color, -25)} 100%);
        }}
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

    def on_button_press(self, widget, event):
        """Handle button press for dragging"""
        if event.button == 1:  # Left click
            self.dragging = True
            x, y = self.window.get_position()
            self.drag_offset_x = event.x_root - x
            self.drag_offset_y = event.y_root - y

    def on_button_release(self, widget, event):
        """Handle button release"""
        if event.button == 1:
            self.dragging = False
            # Save new position
            x, y = self.window.get_position()
            self.config['position_x'] = x
            self.config['position_y'] = y
            self.save_config()

    def on_motion(self, widget, event):
        """Handle mouse motion for dragging"""
        if self.dragging:
            x = int(event.x_root - self.drag_offset_x)
            y = int(event.y_root - self.drag_offset_y)
            self.window.move(x, y)

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
        """Handle button click to open VSCode"""
        # Si no hay directorio detectado, usar alternativas inteligentes
        if not self.current_directory or not os.path.exists(self.current_directory):
            self.current_directory = self.get_smart_directory()
        
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
    
    def try_open_with_editor(self):
        """Try to open with configured editor"""
        try:
            editor_cmd = self.config.get('editor_command', 'code')
            
            # Create the subprocess with proper settings to avoid terminal popup
            process = subprocess.Popen(
                [editor_cmd, self.current_directory],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            
            print(f"Abriendo {self.current_directory} con {editor_cmd}")
            return True
            
        except FileNotFoundError:
            print(f"Editor {self.config.get('editor_command')} no encontrado")
            return False
        except Exception as e:
            print(f"Error abriendo editor: {e}")
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
                        text=True
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
                
                print(f"Abriendo {self.current_directory} con {cmd}")
                # Update config with working command
                self.config['editor_command'] = cmd
                self.save_config()
                return True
                
            except Exception as e:
                continue
        
        return False

    def update_current_directory(self):
        """Update the current directory from active Nautilus window"""
        nautilus_detected = False

        try:
            # Check if Nautilus is running
            check_nautilus = subprocess.run(
                ['pgrep', '-x', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if check_nautilus.returncode != 0:
                # Nautilus no está ejecutándose - pero mantener botón visible por ahora
                print("Nautilus no está ejecutándose")
                self.current_directory = None
                # No ocultar automáticamente - dejar que el usuario decida
                return True

            # Múltiples métodos para detectar la carpeta activa
            directory = self.get_nautilus_directory_multiple_methods()
            
            if directory:
                nautilus_detected = True
                self.current_directory = directory
                print(f"Directorio detectado: {directory}")
                self.update_tooltip()
                
                # Show button if Nautilus is open
                if not self.window.get_visible():
                    print("Mostrando botón - directorio encontrado")
                    self.window.show_all()
            else:
                # No Nautilus windows found or no valid directory
                print("No se detectó directorio válido de Nautilus")
                self.current_directory = None
                # Mantener botón visible

        except Exception as e:
            print(f"Error detectando directorio: {e}")
            # En caso de error, mantener el último directorio conocido
            # No ocultar automáticamente

        return True  # Continue timer

    def get_nautilus_directory_multiple_methods(self):
        """Try multiple methods to get the current Nautilus directory"""
        methods = [
            self.get_directory_from_active_nautilus_window,
            self.get_directory_from_focused_nautilus,
            self.get_directory_from_nautilus_process,
            self.get_directory_from_xdotool,
            self.get_directory_from_wmctrl,
            self.get_directory_from_active_window,
            self.get_directory_from_fallback
        ]
        
        for method in methods:
            try:
                directory = method()
                if directory and os.path.exists(directory):
                    return directory
            except Exception as e:
                continue
        
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
                    print(f"Ventana activa de Nautilus: '{title}'")
                    
                    # Try to get directory from title
                    directory = self.extract_directory_from_title(title)
                    if directory:
                        print(f"Directorio desde ventana activa: {directory}")
                        return directory
                    
                    # If title doesn't have path, try to get it from window properties
                    directory = self.get_directory_from_window_properties(active_window_id)
                    if directory:
                        return directory
            
        except Exception as e:
            print(f"Error detectando ventana activa: {e}")
        
        return None
    
    def get_directory_from_focused_nautilus(self):
        """Get directory from focused Nautilus window using different approach"""
        try:
            # Get all Nautilus windows and find the focused one
            result = subprocess.run(
                ['xdotool', 'search', '--class', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                
                # Get the currently focused window
                focused_result = subprocess.run(
                    ['xdotool', 'getwindowfocus'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if focused_result.returncode == 0:
                    focused_id = focused_result.stdout.strip()
                    
                    # Check if the focused window is one of our Nautilus windows
                    for window_id in window_ids:
                        if window_id.strip() == focused_id:
                            # This is a focused Nautilus window
                            title_result = subprocess.run(
                                ['xdotool', 'getwindowname', window_id.strip()],
                                capture_output=True,
                                text=True,
                                timeout=1
                            )
                            
                            if title_result.returncode == 0:
                                title = title_result.stdout.strip()
                                print(f"Nautilus enfocado: '{title}'")
                                directory = self.extract_directory_from_title(title)
                                if directory:
                                    print(f"Directorio desde ventana enfocada: {directory}")
                                    return directory
                    
                    # If focused window is not Nautilus, get the most recently active Nautilus
                    for window_id in window_ids:
                        if window_id.strip():
                            # Check if window is visible
                            visible_result = subprocess.run(
                                ['xdotool', 'getwindowgeometry', '--shell', window_id.strip()],
                                capture_output=True,
                                text=True,
                                timeout=1
                            )
                            
                            if visible_result.returncode == 0:
                                title_result = subprocess.run(
                                    ['xdotool', 'getwindowname', window_id.strip()],
                                    capture_output=True,
                                    text=True,
                                    timeout=1
                                )
                                
                                if title_result.returncode == 0:
                                    title = title_result.stdout.strip()
                                    directory = self.extract_directory_from_title(title)
                                    if directory:
                                        print(f"Directorio desde Nautilus visible: {directory}")
                                        return directory
            
        except Exception as e:
            print(f"Error detectando Nautilus enfocado: {e}")
        
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
                print(f"Propiedades de ventana: {output}")
                
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
            
        except Exception as e:
            print(f"Error obteniendo propiedades: {e}")
        
        return None
    
    def get_directory_from_nautilus_process(self):
        """Get directory from Nautilus process information"""
        try:
            # Get nautilus process info
            result = subprocess.run(
                ['pgrep', '-a', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    print(f"Proceso Nautilus: {line}")
                    # Look for file:// URLs in process arguments
                    if 'file://' in line:
                        import re
                        urls = re.findall(r'file://([^\s]+)', line)
                        for url in urls:
                            from urllib.parse import unquote
                            path = unquote(url)
                            if os.path.exists(path) and os.path.isdir(path):
                                print(f"Directorio desde proceso: {path}")
                                return path
            
        except Exception as e:
            print(f"Error obteniendo info del proceso: {e}")
        
        return None
    
    def get_directory_from_xdotool(self):
        """Get directory using xdotool with improved detection"""
        try:
            # Get Nautilus window IDs
            result = subprocess.run(
                ['xdotool', 'search', '--class', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                for window_id in window_ids:
                    if window_id.strip():
                        # Get window name for each ID
                        name_result = subprocess.run(
                            ['xdotool', 'getwindowname', window_id.strip()],
                            capture_output=True,
                            text=True,
                            timeout=1
                        )
                        
                        if name_result.returncode == 0:
                            title = name_result.stdout.strip()
                            print(f"Título de ventana detectado: '{title}'")
                            
                            # Try to extract directory from title
                            directory = self.extract_directory_from_title(title)
                            if directory:
                                print(f"Directorio extraído: {directory}")
                                return directory
            
        except Exception as e:
            print(f"Error en xdotool: {e}")
        
        return None
    
    def get_directory_from_wmctrl(self):
        """Get directory using wmctrl"""
        result = subprocess.run(
            ['wmctrl', '-l'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'nautilus' in line.lower() or 'Files' in line or 'Archivos' in line:
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        title = parts[3]
                        directory = self.extract_directory_from_title(title)
                        if directory:
                            return directory
        return None
    
    def get_directory_from_active_window(self):
        """Get directory from currently active window if it's Nautilus"""
        # Get active window
        result = subprocess.run(
            ['xdotool', 'getactivewindow', 'getwindowname'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            title = result.stdout.strip()
            if 'Files' in title or 'Archivos' in title or title.startswith('/'):
                return self.extract_directory_from_title(title)
        return None
    
    def get_directory_from_fallback(self):
        """Fallback method - use smart defaults"""
        try:
            # Try current working directory first
            cwd = os.getcwd()
            if os.path.exists(cwd) and os.path.isdir(cwd):
                print(f"Usando directorio actual: {cwd}")
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
                    print(f"Usando directorio por defecto: {directory}")
                    return directory
            
        except Exception as e:
            print(f"Error en fallback: {e}")
        
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
        
        print(f"Título limpio para búsqueda: '{title}'")

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
                print(f"Detectada carpeta home: {home}")
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
                    print(f"Subcarpeta de home encontrada: {path}")
                    return path
            
            # Enhanced search for folder names
            if '/' not in title and title not in ['org.gnome.Nautilus', 'Nautilus']:
                found_path = self.search_folder_by_name(title)
                if found_path:
                    return found_path

        print(f"No se pudo extraer directorio del título: '{original_title}'")
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
                                print(f"Carpeta encontrada: {full_path}")
                                return full_path
                except PermissionError:
                    continue
        
        # Then try deeper search (max 2 levels)
        for base_dir in search_locations[:3]:  # Only search in home, Documents, Documentos
            if os.path.exists(base_dir):
                try:
                    found = self.recursive_folder_search(base_dir, folder_name, max_depth=2)
                    if found:
                        print(f"Carpeta encontrada (recursiva): {found}")
                        return found
                except Exception as e:
                    continue
        
        return None
    
    def recursive_folder_search(self, base_dir, target_name, max_depth=2, current_depth=0):
        """Recursively search for a folder by name"""
        if current_depth >= max_depth:
            return None
            
        try:
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                
                # Check if this item matches our target
                if os.path.isdir(item_path) and item.lower() == target_name.lower():
                    return item_path
                
                # Recurse into subdirectories
                if os.path.isdir(item_path) and current_depth < max_depth - 1:
                    # Skip hidden directories and common system directories
                    if not item.startswith('.') and item not in ['node_modules', '__pycache__', '.git']:
                        result = self.recursive_folder_search(item_path, target_name, max_depth, current_depth + 1)
                        if result:
                            return result
        
        except PermissionError:
            pass
        
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
            title="Configuración - VSCode Opener",
            parent=None,
            flags=0
        )
        self.dialog.set_default_size(400, 300)
        self.dialog.set_border_width(10)

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

        self.dialog.show_all()

        response = self.dialog.run()

        if response == Gtk.ResponseType.OK:
            self.save_settings()

        self.dialog.destroy()

    def save_settings(self):
        """Save settings and apply changes"""
        # Update config
        self.app.config['editor_command'] = self.editor_entry.get_text()

        rgba = self.color_button.get_rgba()
        self.app.config['button_color'] = f'#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}'

        self.app.config['show_label'] = self.show_label_switch.get_active()

        # Save to file
        self.app.save_config()

        # Restart app to apply changes
        self.show_restart_dialog()

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
