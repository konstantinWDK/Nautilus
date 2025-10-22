#!/usr/bin/env python3
"""
Nautilus Extension: VSCode Opener
Adds a button to the toolbar to open the current directory in VSCode
"""

import os
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Nautilus', '3.0')
from gi.repository import Nautilus, GObject, Gtk, Gio
from typing import List


class VSCodeOpenerExtension(GObject.GObject, Nautilus.MenuProvider):
    """Extension that adds VSCode menu items to Nautilus"""

    def __init__(self):
        super().__init__()

    def get_background_items(self, window, file):
        """Add menu item to background (empty space) context menu"""
        menu_item = Nautilus.MenuItem(
            name="VSCodeOpener::OpenInVSCode",
            label="Abrir en VSCode",
            tip="Abrir esta carpeta en Visual Studio Code"
        )
        menu_item.connect('activate', self._open_vscode, file)
        return [menu_item]
    
    def get_file_items(self, window, files):
        """Add menu item when files/folders are selected"""
        if len(files) != 1:
            return []
            
        file = files[0]
        if not file.is_directory():
            return []
            
        menu_item = Nautilus.MenuItem(
            name="VSCodeOpener::OpenFolderInVSCode", 
            label="Abrir en VSCode",
            tip="Abrir esta carpeta en Visual Studio Code"
        )
        menu_item.connect('activate', self._open_vscode, file)
        return [menu_item]

    def _open_vscode(self, menu_item, file):
        """Open the file/folder in VSCode"""
        if file is None:
            return
            
        path = file.get_location().get_path()
        if not path:
            return
            
        success = self._try_open_with_vscode(path)
        if not success:
            # Show notification if failed
            try:
                from gi.repository import Notify
                Notify.init("VSCode Opener")
                notification = Notify.Notification.new(
                    "VSCode no encontrado",
                    "No se pudo encontrar ninguna instalación de VSCode compatible.",
                    "dialog-error"
                )
                notification.show()
            except:
                print("Error: No se pudo abrir VSCode")

    def _try_open_with_vscode(self, path: str) -> bool:
        """
        Try to open the path with various VSCode installations
        
        Args:
            path: The path to open
            
        Returns:
            True if successful, False otherwise
        """
        if not path or not os.path.exists(path):
            return False
            
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
                
                # Try to open with proper settings to avoid terminal popup
                process = subprocess.Popen(
                    [cmd, path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
                
                return True
                
            except Exception as e:
                continue
        
        return False
