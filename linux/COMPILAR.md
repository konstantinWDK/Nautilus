# Nautilus VSCode Widget - Crear Paquete .deb

## Crear Paquete para Distribuir

```bash
cd linux
make build
```

Esto genera: `nautilus-vscode-widget_1.0.0_all.deb` (**15-20 KB**)

## Ventajas del Paquete .deb

- ✅ **Instalación con doble clic** - Como cualquier programa de Ubuntu
- ✅ **Dependencias automáticas** - APT las instala automáticamente
- ✅ **Tamaño pequeño** - Solo 15-20 KB
- ✅ **Profesional** - Estándar de distribución en Ubuntu/Debian
- ✅ **Fácil de actualizar** - Solo instala el nuevo .deb
- ✅ **Integración perfecta** - Aparece en el menú de aplicaciones

## Para el Usuario Final

El usuario solo necesita:

1. **Descargar** el archivo `.deb`

2. **Instalar**:
   - Doble clic en el archivo `.deb`
   - O por terminal: `sudo dpkg -i nautilus-vscode-widget_1.0.0_all.deb`

3. **Usar**:
   - El programa se inicia automáticamente
   - O ejecutar: `nautilus-vscode-widget`

4. **Desinstalar**:
   ```bash
   sudo apt remove nautilus-vscode-widget
   ```

## Comandos Disponibles

```bash
cd linux

make help       # Ver ayuda
make build      # Crear paquete .deb
make install    # Instalar localmente
make clean      # Limpiar archivos
```

## Más Información

- Ver [linux/README.md](linux/README.md) para documentación técnica
- Ver [DISTRIBUIR.md](DISTRIBUIR.md) para opciones de distribución

---

**Paquete .deb profesional para Ubuntu/Debian** 🚀
