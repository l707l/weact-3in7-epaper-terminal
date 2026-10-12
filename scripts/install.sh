#!/usr/bin/env bash
# Script de instalación automática para WeAct 3.7" E-Paper Terminal en Raspberry Pi OS / Debian
set -e

echo "=== Instalando WeAct 3.7\" E-Paper Terminal (PaperTTY) ==="

# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-pil python3-spidev python3-gpiozero xfonts-terminus fonts-terminus

# 2. Configuración de SPI en /boot/firmware/config.txt o /boot/config.txt
CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if ! grep -q "dtparam=spi=on" "$CONFIG_FILE"; then
    echo "Habilitando SPI en $CONFIG_FILE..."
    echo "dtparam=spi=on" | sudo tee -a "$CONFIG_FILE"
fi

# 3. Directorio de instalación
INSTALL_DIR="/home/q/PaperTTY"
mkdir -p "$INSTALL_DIR/papertty/drivers"

# 4. Copiar archivos
echo "Copiando driver y módulos..."
cp papertty.py "$INSTALL_DIR/papertty/"
cp drivers/drivers_weact3in7.py "$INSTALL_DIR/papertty/drivers/"
cp drivers/drivers_base.py "$INSTALL_DIR/papertty/drivers/"

# 5. Entorno virtual Python
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "Creando virtualenv en $INSTALL_DIR/venv..."
    python3 -m venv --system-site-packages "$INSTALL_DIR/venv"
fi
"$INSTALL_DIR/venv/bin/pip" install -r requirements.txt

# 6. Servicio Systemd
echo "Instalando servicio systemd..."
sudo cp systemd/papertty-terminal.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable papertty-terminal.service
sudo systemctl restart papertty-terminal.service

echo "=== Instalación completada con éxito ==="
echo "Estado del servicio:"
sudo systemctl status papertty-terminal.service --no-pager
