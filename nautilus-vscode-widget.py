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
import cairo
import subprocess
import os
import re
import json


class FloatingButtonApp:
    def __init__(self):
        self.config_file = os.path.expanduser('~/.config/nautilus-vscode-widget/config.json')
        self.load_config()

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

        # Create floating button window
        self.window = Gtk.Window()
        self.window.set_name("floating-button")
        self.window.set_title("VSCode Widget")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_accept_focus(False)

        # Set window size - botón muy compacto
        self.button_size = 36
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

        # Connect draw signal for transparency
        self.window.connect('draw', self.on_draw)

        # Create button
        self.create_button()

        # Create favorites container
        self.create_favorites_container()

        # Apply CSS
        self.apply_styles()

        # Apply circular shape after window is realized
        self.window.connect('realize', self.apply_circular_shape)

        # Enable dragging
        self.window.connect('button-press-event', self.on_button_press)
        self.window.connect('button-release-event', self.on_button_release)
        self.window.connect('motion-notify-event', self.on_motion)
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)

        # Start monitoring Nautilus windows and focus
        GLib.timeout_add(500, self.update_current_directory)
        GLib.timeout_add(200, self.check_nautilus_focus)

        self.window.connect('destroy', Gtk.main_quit)

        # Show window but start with opacity 0 - let the timer handle visibility
        self.window.show_all()

        # Ocultar todo inicialmente
        self.set_window_opacity(0.0)
        self.window_opacity = 0.0
        self.is_nautilus_focused = False

        # Posicionar botones secundarios después de que la ventana esté visible
        # Se hará en el primer fade_in()

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

    def on_draw(self, widget, cr):
        """Draw transparent background"""
        cr.set_source_rgba(0, 0, 0, 0)  # Completely transparent
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

    def on_draw_overlay(self, widget, cr):
        """Draw transparent overlay background"""
        cr.set_source_rgba(0, 0, 0, 0)  # Completely transparent
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

    def apply_circular_shape(self, widget):
        """Apply circular shape to the window to remove square background"""
        # Create a circular region
        width = self.button_size
        height = self.button_size
        radius = self.button_size // 2

        # Create a cairo surface to draw the shape
        surface = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
        cr = cairo.Context(surface)

        # Draw a filled circle
        cr.set_source_rgba(1, 1, 1, 1)
        cr.arc(radius, radius, radius, 0, 2 * 3.14159)
        cr.fill()

        # Create region from the surface
        region = Gdk.cairo_region_create_from_surface(surface)

        # Apply the shape to the window
        if self.window.get_window():
            self.window.get_window().shape_combine_region(region, 0, 0)
            # Also apply to input shape so clicks outside circle don't register
            self.window.get_window().input_shape_combine_region(region, 0, 0)

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'position_x': 100,
            'position_y': 100,
            'editor_command': 'code',
            'button_color': '#2C2C2C',
            'show_label': False,
            'autostart': False,
            'always_visible': False,  # Mostrar siempre el widget
            'favorite_folders': [],  # Lista de carpetas favoritas
            'favorite_colors': {}  # Diccionario de colores para carpetas favoritas
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
        overlay.set_app_paintable(True)
        overlay.connect('draw', self.on_draw_overlay)
        self.window.add(overlay)

        # Button
        self.button = Gtk.Button()
        self.button.set_size_request(self.button_size, self.button_size)
        self.button.set_relief(Gtk.ReliefStyle.NONE)

        # Button content - diseño compacto
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        # Try to load VSCode icon, fallback to SVG or emoji
        icon_loaded = False
        try:
            # Try to load VSCode icon from system
            icon_theme = Gtk.IconTheme.get_default()
            vscode_icon_names = [
                'com.visualstudio.code',
                'vscode',
                'visual-studio-code',
                'code'
            ]

            for icon_name in vscode_icon_names:
                if icon_theme.has_icon(icon_name):
                    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
                    icon.set_pixel_size(24)
                    box.pack_start(icon, True, True, 0)
                    icon_loaded = True
                    break
        except Exception as e:
            print(f"No se pudo cargar icono del sistema: {e}")

        # If icon not found, try custom SVG path
        if not icon_loaded:
            custom_icon_paths = [
                '/usr/share/pixmaps/vscode.png',
                '/usr/share/icons/hicolor/256x256/apps/code.png',
                '/var/lib/snapd/desktop/applications/code_code.desktop',
                os.path.expanduser('~/.local/share/icons/vscode.png')
            ]

            for icon_path in custom_icon_paths:
                if os.path.exists(icon_path):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 24, 24, True)
                        icon = Gtk.Image.new_from_pixbuf(pixbuf)
                        box.pack_start(icon, True, True, 0)
                        icon_loaded = True
                        break
                    except Exception as e:
                        print(f"Error cargando {icon_path}: {e}")

        # Final fallback: use a styled emoji
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

        overlay.add(self.button)

        # Tooltip
        self.update_tooltip()

    def create_favorites_container(self):
        """Crear contenedor unificado para botones favoritos"""
        # Crear ventana para el contenedor de favoritos
        self.favorites_window = Gtk.Window()
        self.favorites_window.set_decorated(False)
        self.favorites_window.set_keep_above(True)
        self.favorites_window.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.favorites_window.set_skip_taskbar_hint(True)
        self.favorites_window.set_skip_pager_hint(True)
        self.favorites_window.set_accept_focus(False)
        self.favorites_window.set_app_paintable(True)
        self.favorites_window.set_name("favorites-container")

        # Tamaño del contenedor - se ajustará dinámicamente
        self.favorites_window.set_default_size(60, 60)
        self.favorites_window.set_resizable(False)

        # Transparencia
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual:
            self.favorites_window.set_visual(visual)

        self.favorites_window.connect('draw', self.on_draw)

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
            print(f"Error en _post_rebuild_updates: {e}")
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

    def create_add_button(self, overlay):
        """Función legacy - usa rebuild_favorites_list en su lugar"""
        self.create_add_button_internal()

    def create_favorite_buttons(self, overlay):
        """Función legacy - usa rebuild_favorites_list en su lugar"""
        self.rebuild_favorites_list()

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

    def apply_small_circular_shape(self, widget, size):
        """Aplicar forma circular a ventanas pequeñas"""
        radius = size // 2
        surface = cairo.ImageSurface(cairo.FORMAT_A1, size, size)
        cr = cairo.Context(surface)
        cr.set_source_rgba(1, 1, 1, 1)
        cr.arc(radius, radius, radius, 0, 2 * 3.14159)
        cr.fill()
        region = Gdk.cairo_region_create_from_surface(surface)
        if widget.get_window():
            widget.get_window().shape_combine_region(region, 0, 0)
            widget.get_window().input_shape_combine_region(region, 0, 0)

    def update_favorite_positions(self):
        """Actualizar las posiciones de los botones favoritos y el botón +"""
        if not hasattr(self, 'favorites_window'):
            return

        # Calcular tamaño del contenedor basado en número de botones
        num_buttons = len(self.favorite_buttons)

        # Siempre mostrar el contenedor
        self.favorites_window.show()

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

        # Posicionar encima del botón principal con separación adecuada
        # Aumentar la separación para evitar superposición
        separation = 12 if num_buttons == 0 else 8  # Más separación cuando solo está el botón +
        container_y = main_y - container_height - separation

        self.favorites_window.move(container_x, container_y)

        # Aplicar opacidad al contenedor de favoritos
        self.set_widget_opacity(self.favorites_window, self.window_opacity)

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
                border-radius: 14px;
                background: linear-gradient(135deg, rgba({fav_r}, {fav_g}, {fav_b}, 0.9), rgba({fav_r}, {fav_g}, {fav_b}, 0.7));
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 255, 255, 0.1);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 0;
                margin: 0;
            }}

        #fav-button-{i}:hover {{
            background: linear-gradient(135deg, rgba({fav_r}, {fav_g}, {fav_b}, 1.0), rgba({fav_r}, {fav_g}, {fav_b}, 0.8));
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        #fav-button-{i}:active {{
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            background: linear-gradient(135deg, rgba({fav_r}, {fav_g}, {fav_b}, 0.8), rgba({fav_r}, {fav_g}, {fav_b}, 0.6));
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
            background: linear-gradient(135deg, rgba(40, 40, 45, 0.95), rgba(35, 35, 40, 0.85));
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }}

        /* Botón principal con efecto glassmorphism */
        #floating-button button {{
            border-radius: 20px;
            background: linear-gradient(135deg, rgba({r}, {g}, {b}, 0.95), rgba({r}, {g}, {b}, 0.8));
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0;
            margin: 0;
        }}

        #floating-button button:hover {{
            background: linear-gradient(135deg, rgba({r}, {g}, {b}, 1.0), rgba({r}, {g}, {b}, 0.9));
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.35);
        }}

        #floating-button button:active {{
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            background: linear-gradient(135deg, rgba({r}, {g}, {b}, 0.85), rgba({r}, {g}, {b}, 0.7));
        }}

        /* Botón + de añadir favoritos - minimalista y discreto */
        #add-fav-button {{
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(60, 60, 65, 0.7), rgba(50, 50, 55, 0.6));
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
            background: linear-gradient(135deg, rgba(80, 80, 85, 0.9), rgba(70, 70, 75, 0.8));
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.25);
            opacity: 1.0;
        }}

        #add-fav-button:active {{
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.05);
            background: linear-gradient(135deg, rgba(50, 50, 55, 0.75), rgba(40, 40, 45, 0.65));
            opacity: 0.9;
        }}

        /* Botones de carpetas favoritas por defecto */
        #fav-button {{
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(30, 30, 35, 0.9), rgba(25, 25, 30, 0.7));
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
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
            background: linear-gradient(135deg, rgba(40, 40, 45, 1.0), rgba(35, 35, 40, 0.8));
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        #fav-button:active {{
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            background: linear-gradient(135deg, rgba(25, 25, 30, 0.8), rgba(20, 20, 25, 0.6));
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
            # No capturar el evento para permitir que se propague
            return False
        elif event.button == 3:  # Right click
            return self.on_button_right_click(widget, event)
        return False

    def on_button_release_event(self, widget, event):
        """Handle button release on the main button"""
        if event.button == 1:
            # Check if it was a drag or a click
            if self.dragging:
                drag_distance = ((event.x_root - self.drag_start_x) ** 2 +
                               (event.y_root - self.drag_start_y) ** 2) ** 0.5

                if drag_distance < 5:  # Less than 5 pixels = click, not drag
                    # It's a click, trigger the button action
                    self.dragging = False
                    return False  # Let the clicked signal handle it
                else:
                    # It was a drag
                    self.dragging = False
                    # Save new position
                    x, y = self.window.get_position()
                    self.config['position_x'] = x
                    self.config['position_y'] = y
                    self.save_config()
                    return True  # Prevent clicked signal
        return False

    def on_button_motion(self, widget, event):
        """Handle mouse motion on the button for dragging"""
        if self.dragging:
            x = int(event.x_root - self.drag_offset_x)
            y = int(event.y_root - self.drag_offset_y)
            self.window.move(x, y)
            # Actualizar posiciones de botones favoritos y botón de añadir
            self.update_favorite_positions()
            return True
        return False

    def on_button_press(self, widget, event):
        """Handle button press for dragging on window"""
        if event.button == 1:  # Left click
            self.dragging = True
            x, y = self.window.get_position()
            self.drag_offset_x = event.x_root - x
            self.drag_offset_y = event.y_root - y

    def on_button_release(self, widget, event):
        """Handle button release on window"""
        if event.button == 1:
            self.dragging = False
            # Save new position
            x, y = self.window.get_position()
            self.config['position_x'] = x
            self.config['position_y'] = y
            self.save_config()

    def on_motion(self, widget, event):
        """Handle mouse motion for dragging on window"""
        if self.dragging:
            x = int(event.x_root - self.drag_offset_x)
            y = int(event.y_root - self.drag_offset_y)
            self.window.move(x, y)
            # Actualizar posiciones de botones favoritos y botón de añadir
            self.update_favorite_positions()

    def check_nautilus_focus(self):
        """Check if Nautilus window is currently focused and has valid directory"""
        # Si está configurado para mostrar siempre, mantener visible
        if self.config.get('always_visible', False):
            if not self.is_nautilus_focused or self.window_opacity < 1.0:
                self.is_nautilus_focused = True
                self.fade_in()
            return True

        try:
            # Get the active window ID first
            window_id_result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if window_id_result.returncode != 0:
                if self.is_nautilus_focused:
                    self.is_nautilus_focused = False
                    self.fade_out()
                return True

            window_id = window_id_result.stdout.strip()

            # Get window class using xprop
            class_result = subprocess.run(
                ['xprop', '-id', window_id, 'WM_CLASS'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if class_result.returncode == 0:
                window_class = class_result.stdout.strip().lower()
                nautilus_focused = 'nautilus' in window_class

                # Check if we should show the button
                has_directory = self.current_directory and os.path.exists(self.current_directory)
                should_show = nautilus_focused and has_directory

                # If focus state changed
                if should_show != self.is_nautilus_focused:
                    self.is_nautilus_focused = should_show

                    if should_show:
                        self.fade_in()
                    else:
                        self.fade_out()

        except Exception:
            # If xdotool fails, hide button to be safe
            if self.is_nautilus_focused:
                self.is_nautilus_focused = False
                self.fade_out()

        return True  # Continue timer

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

    def animate_favorites_expand(self):
        """Mostrar botones favoritos sin animaciones"""
        # Sin animaciones - simplemente actualizar posiciones
        self.update_favorite_positions()

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
            
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
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
        try:
            # Check if Nautilus is running
            check_nautilus = subprocess.run(
                ['pgrep', '-x', 'nautilus'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if check_nautilus.returncode != 0:
                # Nautilus no está ejecutándose
                self.current_directory = None
                self.update_tooltip()
                return True

            # Múltiples métodos para detectar la carpeta activa
            directory = self.get_nautilus_directory_multiple_methods()

            if directory:
                if directory != self.current_directory:
                    self.current_directory = directory
                    self.update_tooltip()
            else:
                # No se detectó directorio válido
                self.current_directory = None
                self.update_tooltip()

        except Exception:
            self.current_directory = None

        return True  # Continue timer

    def get_nautilus_directory_multiple_methods(self):
        """Try multiple methods to get the current Nautilus directory"""
        methods = [
            self.get_directory_from_dbus,  # Más confiable para Nautilus moderno
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
                                directory = self.extract_directory_from_title(title)
                                if directory:
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
                    # Look for file:// URLs in process arguments
                    if 'file://' in line:
                        import re
                        urls = re.findall(r'file://([^\s]+)', line)
                        for url in urls:
                            from urllib.parse import unquote
                            path = unquote(url)
                            if os.path.exists(path) and os.path.isdir(path):
                                return path

        except Exception:
            pass
        
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

                            # Try to extract directory from title
                            directory = self.extract_directory_from_title(title)
                            if directory:
                                return directory

        except Exception:
            pass
        
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

        # Always visible option
        always_visible_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        always_visible_label = Gtk.Label(label="Mostrar siempre:")
        always_visible_label.set_width_chars(20)
        always_visible_label.set_xalign(0)
        self.always_visible_switch = Gtk.Switch()
        self.always_visible_switch.set_active(self.app.config.get('always_visible', False))
        always_visible_box.pack_start(always_visible_label, False, False, 0)
        always_visible_box.pack_start(self.always_visible_switch, False, False, 0)
        box.pack_start(always_visible_box, False, False, 0)

        # Always visible info
        always_visible_info = Gtk.Label()
        always_visible_info.set_markup('<span font="8" style="italic">💡 El botón estará visible siempre, no solo con Nautilus</span>')
        always_visible_info.set_xalign(0)
        always_visible_info.set_margin_start(20)
        box.pack_start(always_visible_info, False, False, 0)

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

        # Handle always visible
        self.app.config['always_visible'] = self.always_visible_switch.get_active()

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
            desktop_file = os.path.expanduser('~/.config/autostart/nautilus-vscode-widget.desktop')
            return os.path.exists(desktop_file)
        except Exception as e:
            print(f"Error verificando autostart: {e}")
            return False

    def enable_autostart(self):
        """Enable autostart by creating .desktop file"""
        try:
            autostart_dir = os.path.expanduser('~/.config/autostart')
            if not os.path.exists(autostart_dir):
                os.makedirs(autostart_dir)

            desktop_file = os.path.join(autostart_dir, 'nautilus-vscode-widget.desktop')
            script_path = os.path.abspath(__file__)

            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Nautilus VSCode Widget
Comment=Floating button to open folders in VSCode from Nautilus
Exec=python3 "{script_path}"
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

            print(f"Autostart habilitado: {desktop_file}")

        except Exception as e:
            print(f"Error habilitando autostart: {e}")

    def disable_autostart(self):
        """Disable autostart by removing .desktop file"""
        try:
            desktop_file = os.path.expanduser('~/.config/autostart/nautilus-vscode-widget.desktop')
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
                print("Autostart deshabilitado")
        except Exception as e:
            print(f"Error deshabilitando autostart: {e}")

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
