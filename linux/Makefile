.PHONY: help build clean install

help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════╗"
	@echo "║     Nautilus VSCode Opener - Paquete .deb                    ║"
	@echo "╚═══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make build      - Crear paquete .deb"
	@echo "  make install    - Instalar el paquete .deb"
	@echo "  make clean      - Limpiar archivos generados"
	@echo ""
	@echo "Para más información, ver: README.md"
	@echo ""

build:
	@./build-deb.sh

install:
	@if [ -f *.deb ]; then \
		echo "Instalando paquete .deb..."; \
		sudo dpkg -i *.deb; \
		echo "¡Instalación completada!"; \
	else \
		echo "Error: No se encuentra el paquete .deb"; \
		echo "Ejecuta primero: make build"; \
		exit 1; \
	fi

clean:
	@echo "Limpiando archivos generados..."
	@rm -rf debian/usr/
	@rm -f *.deb
	@echo "✓ Limpieza completada"
