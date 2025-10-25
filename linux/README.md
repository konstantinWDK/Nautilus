# Nautilus VSCode Widget - Paquete .deb

Sistema de empaquetado profesional para Ubuntu/Debian.

## Para Desarrolladores

### Crear paquete .deb

```bash
make build
```

Esto genera: `nautilus-vscode-widget_1.0.0_all.deb` (~15-20 KB)

### Instalar localmente

```bash
make install
```

O manualmente:

```bash
sudo dpkg -i nautilus-vscode-widget_1.0.0_all.deb
```

### Limpiar archivos

```bash
make clean
```

## Para Usuarios Finales

### Instalación

**Opción 1: Doble clic**
- Descarga el archivo `.deb`
- Haz doble clic sobre él
- Se abrirá el Centro de Software
- Haz clic en "Instalar"

**Opción 2: Terminal**

```bash
sudo dpkg -i nautilus-vscode-widget_1.0.0_all.deb
```

Si faltan dependencias:

```bash
sudo apt --fix-broken install
```

### Uso

El programa se inicia automáticamente con tu sesión.

O inicia manualmente:

```bash
nautilus-vscode-widget
```

### Desinstalación

```bash
sudo apt remove nautilus-vscode-widget
```

## Características del Paquete .deb

- ✅ **Instalación con doble clic** - Como cualquier programa
- ✅ **Dependencias automáticas** - APT las instala automáticamente
- ✅ **Integración con el sistema** - Aparece en aplicaciones
- ✅ **Desinstalación limpia** - Elimina todo correctamente
- ✅ **Actualización fácil** - Solo instala el nuevo .deb
- ✅ **Tamaño pequeño** - Solo 15-20 KB

## Dependencias

El paquete .deb especifica estas dependencias (se instalan automáticamente):

- python3
- python3-gi
- python3-gi-cairo
- gir1.2-gtk-3.0
- xdotool
- wmctrl

## Estructura del Paquete

```
nautilus-vscode-widget_1.0.0_all.deb
├── DEBIAN/
│   ├── control       # Metadatos del paquete
│   ├── postinst      # Script post-instalación
│   └── prerm         # Script pre-eliminación
├── usr/
│   ├── bin/
│   │   └── nautilus-vscode-widget  # Lanzador
│   ├── share/
│   │   ├── nautilus-vscode-widget/
│   │   │   └── nautilus-vscode-widget.py  # Programa
│   │   ├── applications/
│   │   │   └── nautilus-vscode-widget.desktop
│   │   └── doc/
│   │       └── nautilus-vscode-widget/
│   │           └── copyright
```

## Ubicaciones Después de Instalar

- **Programa**: `/usr/share/nautilus-vscode-widget/`
- **Ejecutable**: `/usr/bin/nautilus-vscode-widget`
- **Desktop**: `/usr/share/applications/`
- **Autostart**: `~/.config/autostart/nautilus-vscode-widget.desktop` (creado automáticamente)
- **Configuración**: `~/.config/nautilus-vscode-widget/config.json`

## Distribución

### Subir a GitHub Releases

```bash
gh release create v1.0.0 \
  nautilus-vscode-widget_1.0.0_all.deb \
  --title "Nautilus VSCode Widget v1.0.0" \
  --notes "Paquete .deb para Ubuntu/Debian"
```

### Compartir

El archivo `.deb` puede compartirse directamente:
- GitHub Releases
- Sitio web personal
- Foros de Ubuntu
- Reddit (r/Ubuntu, r/linux)

## Ventajas del .deb

| Característica | Valor |
|----------------|-------|
| Instalación | Doble clic |
| Dependencias | Automáticas |
| Integración | Sistema completo |
| Tamaño | 15-20 KB |
| Actualización | Fácil |
| Desinstalación | Limpia |

## Comandos Make

```bash
make help       # Ver ayuda
make build      # Crear paquete .deb
make install    # Instalar paquete
make clean      # Limpiar archivos
```

---

**Paquete .deb profesional para Ubuntu/Debian** 🚀
