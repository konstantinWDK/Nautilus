#!/usr/bin/env python3
"""
Nautilus Extension: VSCode Floating Button (Smart Approach)
Creates a floating button that appears over Nautilus windows
"""

import os
import subprocess
import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
except ValueError:
    pass
from gi.repository import Nautilus, GObject, Gtk, Gdk, GLib


class VSCodeSmartFloatingExtension(GObject.GObject, Nautilus.MenuProvider):
    """Extension that creates a smart floating button overlay"""

    def __init__(self):
        super().__init__()
        self.floating_windows = {}
        self.timer_id = None
        self.start_monitoring()

    def get_background_items(self, window, file):
        """Trigger overlay creation when background is accessed"""
        self._ensure_floating_button_for_window(window, file)
        return []

    def start_monitoring(self):
        """Start monitoring for Nautilus windows"""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        self.timer_id = GLib.timeout_add(1000, self._monitor_nautilus_windows)

    def _monitor_nautilus_windows(self):
        """Monitor for new Nautilus windows and add floating buttons"""
        try:
            # Get all toplevel windows
            for window in Gtk.Window.list_toplevels():
                if self._is_nautilus_window(window):
                    window_id = id(window)
                    if window_id not in self.floating_windows:
                        self._create_floating_button_for_window(window)
        except Exception as e:
            print(f"Error monitoring windows: {e}")
        
        return True  # Continue monitoring

    def _is_nautilus_window(self, window):
        """Check if window is a Nautilus window"""
        try:
            title = window.get_title()
            if not title:
                return False
            
            # Check for Nautilus window indicators
            nautilus_indicators = ['Files', 'Archivos', '/home/', '/usr/', '/var/', '/opt/']
            for indicator in nautilus_indicators:
                if indicator in title:
                    return True
            
            # Check window class
            if hasattr(window, 'get_application'):
                app = window.get_application()
                if app and hasattr(app, 'get_application_id'):
                    app_id = app.get_application_id()
                    if app_id and 'nautilus' in app_id.lower():
                        return True
            
            return False
        except Exception:
            return False

    def _create_floating_button_for_window(self, nautilus_window):
        """Create floating button overlay for a Nautilus window"""
        try:
            window_id = id(nautilus_window)
            
            # Create overlay window
            overlay_window = Gtk.Window()
            overlay_window.set_decorated(False)
            overlay_window.set_type_hint(Gdk.WindowTypeHint.TOOLTIP)
            overlay_window.set_skip_taskbar_hint(True)
            overlay_window.set_skip_pager_hint(True)
            overlay_window.set_accept_focus(False)
            overlay_window.set_app_paintable(True)
            
            # Make it transparent
            screen = overlay_window.get_screen()
            visual = screen.get_rgba_visual()
            if visual:
                overlay_window.set_visual(visual)
            
            # Create the button
            button = self._create_vscode_button(nautilus_window)
            overlay_window.add(button)
            
            # Position overlay over the Nautilus window
            self._position_overlay(overlay_window, nautilus_window)
            
            # Store reference
            self.floating_windows[window_id] = {
                'nautilus_window': nautilus_window,
                'overlay_window': overlay_window,
                'button': button
            }
            
            # Connect window destroy signal
            nautilus_window.connect('destroy', self._on_nautilus_window_destroyed, window_id)
            
            # Show overlay
            overlay_window.show_all()
            
            # Update position periodically
            GLib.timeout_add(500, self._update_overlay_position, window_id)
            
        except Exception as e:
            print(f"Error creating floating button: {e}")

    def _create_vscode_button(self, nautilus_window):
        """Create the VSCode button widget"""
        button = Gtk.Button()
        button.set_size_request(60, 60)
        button.set_relief(Gtk.ReliefStyle.NONE)
        
        # Button content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon_label = Gtk.Label()
        icon_label.set_markup('<span font="20">💻</span>')
        box.pack_start(icon_label, False, False, 0)
        
        # Label
        label = Gtk.Label()
        label.set_markup('<span font="7" weight="bold" color="white">VS Code</span>')
        box.pack_start(label, False, False, 0)
        
        button.add(box)
        
        # Apply styles
        self._apply_floating_button_styles(button)
        
        # Set tooltip
        button.set_tooltip_text("Abrir carpeta actual en VSCode")
        
        # Connect click event
        button.connect('clicked', self._on_floating_button_clicked, nautilus_window)
        
        return button

    def _apply_floating_button_styles(self, button):
        """Apply floating button styles"""
        css_provider = Gtk.CssProvider()
        css = b"""
        button {
            border-radius: 30px;
            background: linear-gradient(145deg, #007ACC 0%, #005A9E 100%);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: linear-gradient(145deg, #008AE6 0%, #0066B8 100%);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            border: 2px solid rgba(255, 255, 255, 0.6);
            transform: scale(1.1);
        }
        
        button:active {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            background: linear-gradient(145deg, #005A9E 0%, #004080 100%);
        }
        """
        css_provider.load_from_data(css)
        
        context = button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _position_overlay(self, overlay_window, nautilus_window):
        """Position overlay window over Nautilus window"""
        try:
            # Get Nautilus window position and size
            x, y = nautilus_window.get_position()
            width, height = nautilus_window.get_size()
            
            # Position overlay in top-right corner
            overlay_x = x + width - 80  # 80px from right edge
            overlay_y = y + 40  # 40px from top
            
            overlay_window.move(overlay_x, overlay_y)
            overlay_window.resize(60, 60)
            
        except Exception as e:
            print(f"Error positioning overlay: {e}")

    def _update_overlay_position(self, window_id):
        """Update overlay position to follow Nautilus window"""
        try:
            if window_id not in self.floating_windows:
                return False
                
            window_data = self.floating_windows[window_id]
            nautilus_window = window_data['nautilus_window']
            overlay_window = window_data['overlay_window']
            
            # Check if Nautilus window still exists
            if not nautilus_window.get_visible():
                return False
                
            # Update position
            self._position_overlay(overlay_window, nautilus_window)
            
            return True  # Continue updating
            
        except Exception as e:
            print(f"Error updating position: {e}")
            return False

    def _on_floating_button_clicked(self, button, nautilus_window):
        """Handle floating button click"""
        try:
            # Get current directory from Nautilus window title
            title = nautilus_window.get_title()
            path = self._extract_path_from_title(title)
            
            if not path:
                # Fallback: use home directory
                path = os.path.expanduser('~')
            
            success = self._open_vscode(path)
            if not success:
                self._show_error_notification()
                
        except Exception as e:
            print(f"Error handling button click: {e}")

    def _extract_path_from_title(self, title):
        """Extract directory path from Nautilus window title"""
        if not title:
            return None
            
        # Remove "Files" or "Archivos" prefix
        for prefix in ['Files - ', 'Archivos - ', 'Files', 'Archivos']:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # If it's a path, return it
        if title.startswith('/'):
            return title if os.path.exists(title) else None
        
        # Try common folder mappings
        home = os.path.expanduser('~')
        folder_mappings = {
            'Documents': os.path.join(home, 'Documents'),
            'Documentos': os.path.join(home, 'Documents'),
            'Downloads': os.path.join(home, 'Downloads'),
            'Descargas': os.path.join(home, 'Downloads'),
            'Pictures': os.path.join(home, 'Pictures'),
            'Imágenes': os.path.join(home, 'Pictures'),
        }
        
        for folder_name, folder_path in folder_mappings.items():
            if folder_name in title and os.path.exists(folder_path):
                return folder_path
        
        return home

    def _open_vscode(self, path):
        """Open VSCode with the given path"""
        vscode_commands = [
            'code', 'code-insiders', 'codium', 'vscodium',
            '/usr/bin/code', '/snap/bin/code'
        ]
        
        for cmd in vscode_commands:
            try:
                if cmd.startswith('/'):
                    if not os.path.isfile(cmd) or not os.access(cmd, os.X_OK):
                        continue
                else:
                    check = subprocess.run(['which', cmd], capture_output=True)
                    if check.returncode != 0:
                        continue
                
                subprocess.Popen(
                    [cmd, path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )
                return True
                
            except Exception:
                continue
        
        return False

    def _show_error_notification(self):
        """Show error notification"""
        try:
            from gi.repository import Notify
            Notify.init("VSCode Opener")
            notification = Notify.Notification.new(
                "VSCode no encontrado",
                "Instala VSCode para usar esta función",
                "dialog-error"
            )
            notification.show()
        except:
            print("Error: VSCode no encontrado")

    def _on_nautilus_window_destroyed(self, window, window_id):
        """Clean up when Nautilus window is destroyed"""
        if window_id in self.floating_windows:
            overlay_window = self.floating_windows[window_id]['overlay_window']
            overlay_window.destroy()
            del self.floating_windows[window_id]

    def _ensure_floating_button_for_window(self, window, file):
        """Ensure floating button exists for given window"""
        # This is called from the menu provider interface
        # We'll use it as a trigger to create overlay if needed
        pass