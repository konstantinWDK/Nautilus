#!/usr/bin/env python3
"""
Nautilus Extension: VSCode Floating Button Widget
Adds a floating button widget inside Nautilus windows
"""

import os
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject, Gtk, Gdk


class VSCodeFloatingButtonExtension(GObject.GObject, Nautilus.InfoProvider):
    """Extension that adds a floating button widget inside Nautilus"""

    def __init__(self):
        super().__init__()

    def update_file_info(self, file):
        """Called for each file - we'll use this to inject our widget"""
        return Nautilus.OperationResult.COMPLETE


class VSCodeWidgetProvider(GObject.GObject, Nautilus.PropertyPageProvider):
    """Provider for the floating widget"""

    def __init__(self):
        super().__init__()
        self.current_location = None

    def get_property_pages(self, files):
        """This won't be used but required for the interface"""
        return []


class VSCodeOverlayExtension(GObject.GObject, Nautilus.MenuProvider):
    """Extension that creates overlay widgets in Nautilus"""

    def __init__(self):
        super().__init__()
        self.widgets = {}
        
    def get_background_items(self, window, file):
        """Hook into background to inject our widget"""
        self._inject_floating_button(window, file)
        return []
    
    def _inject_floating_button(self, window, file):
        """Inject floating button into the Nautilus window"""
        try:
            # Get the Nautilus window widget
            nautilus_window = self._find_nautilus_window_widget(window)
            if not nautilus_window:
                return
                
            # Check if we already have a button for this window
            window_id = id(nautilus_window)
            if window_id in self.widgets:
                return
            
            # Create overlay container
            overlay = Gtk.Overlay()
            
            # Get the current content and reparent it
            child = nautilus_window.get_child()
            if child:
                nautilus_window.remove(child)
                overlay.add(child)
            
            # Create floating button
            button = self._create_floating_button(file)
            
            # Position button in top-right corner
            button.set_halign(Gtk.Align.END)
            button.set_valign(Gtk.Align.START)
            button.set_margin_top(20)
            button.set_margin_end(20)
            
            # Add button as overlay
            overlay.add_overlay(button)
            
            # Add overlay to window
            nautilus_window.add(overlay)
            
            # Store reference
            self.widgets[window_id] = {
                'overlay': overlay,
                'button': button,
                'file': file
            }
            
            # Show everything
            overlay.show_all()
            button.show_all()
            
        except Exception as e:
            print(f"Error injecting floating button: {e}")
    
    def _find_nautilus_window_widget(self, window):
        """Find the actual GTK window widget"""
        try:
            # This is tricky - we need to find the actual GTK widget
            # The window parameter is a Nautilus.Window, not a Gtk.Window
            
            # Try to get the toplevel widget
            if hasattr(window, 'get_toplevel'):
                return window.get_toplevel()
            
            # Alternative approach - find by walking widget hierarchy
            import gi.repository.Gtk as Gtk
            for widget in Gtk.Window.list_toplevels():
                if widget.get_title() and ('Files' in widget.get_title() or 'Archivos' in widget.get_title()):
                    return widget
            
            return None
        except Exception as e:
            print(f"Error finding Nautilus window: {e}")
            return None
    
    def _create_floating_button(self, file):
        """Create the floating VSCode button"""
        # Main button
        button = Gtk.Button()
        button.set_size_request(60, 60)
        button.set_relief(Gtk.ReliefStyle.NONE)
        
        # Button content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        try:
            icon = Gtk.Image.new_from_icon_name("com.visualstudio.code", Gtk.IconSize.LARGE_TOOLBAR)
        except:
            icon = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        
        box.pack_start(icon, False, False, 0)
        
        # Label
        label = Gtk.Label()
        label.set_markup('<span font="8" weight="bold">VS Code</span>')
        box.pack_start(label, False, False, 0)
        
        button.add(box)
        
        # Styling
        self._apply_button_styles(button)
        
        # Tooltip
        button.set_tooltip_text("Abrir en VSCode")
        
        # Connect click event
        button.connect('clicked', self._on_button_clicked, file)
        
        return button
    
    def _apply_button_styles(self, button):
        """Apply CSS styles to make button look floating"""
        css_provider = Gtk.CssProvider()
        css = b"""
        button {
            border-radius: 30px;
            background: linear-gradient(145deg, #007ACC 0%, #005A9E 100%);
            color: white;
            border: 3px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: linear-gradient(145deg, #008AE6 0%, #0066B8 100%);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
            border: 3px solid rgba(255, 255, 255, 0.5);
            transform: scale(1.05);
        }
        
        button:active {
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, #005A9E 0%, #004080 100%);
        }
        """
        css_provider.load_from_data(css)
        
        context = button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def _on_button_clicked(self, button, file):
        """Handle button click"""
        if not file:
            return
            
        path = file.get_location().get_path()
        if not path:
            return
            
        success = self._try_open_with_vscode(path)
        if not success:
            # Show error notification
            try:
                from gi.repository import Notify
                Notify.init("VSCode Opener")
                notification = Notify.Notification.new(
                    "VSCode no encontrado",
                    "No se pudo encontrar VSCode instalado",
                    "dialog-error"
                )
                notification.show()
            except:
                print("Error: VSCode no encontrado")
    
    def _try_open_with_vscode(self, path):
        """Try to open path with VSCode"""
        vscode_commands = [
            'code',
            'code-insiders', 
            'codium',
            'vscodium',
            '/usr/bin/code',
            '/usr/local/bin/code',
            '/snap/bin/code',
            '/var/lib/flatpak/app/com.visualstudio.code/current/active/export/bin/com.visualstudio.code',
            '/opt/visual-studio-code/bin/code'
        ]
        
        for cmd in vscode_commands:
            try:
                if cmd.startswith('/'):
                    if not os.path.isfile(cmd) or not os.access(cmd, os.X_OK):
                        continue
                else:
                    check_cmd = subprocess.run(['which', cmd], capture_output=True, text=True)
                    if check_cmd.returncode != 0:
                        continue
                
                subprocess.Popen(
                    [cmd, path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
                return True
                
            except Exception:
                continue
        
        return False