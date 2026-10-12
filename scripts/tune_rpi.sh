#!/usr/bin/env bash
set -e

echo "=== Aplicando optimizaciones de hardware para PaperTTY ==="

# 1. SPI Buffer Size a 65536 bytes (Transferencias DMA continuas sin fragmentación)
echo 'options spidev bufsiz=65536' > /etc/modprobe.d/spidev.conf

# 2. Evitar que la consola Linux se apague tras inactividad (consoleblank=0)
CMDLINE="/boot/firmware/cmdline.txt"
if [ ! -f "$CMDLINE" ]; then CMDLINE="/boot/cmdline.txt"; fi

if ! grep -q "consoleblank=0" "$CMDLINE"; then
    python3 -c "
p = '$CMDLINE'
with open(p, 'r') as f:
    content = f.read().strip()
with open(p, 'w') as f:
    f.write(content + ' consoleblank=0\n')
"
    echo "consoleblank=0 agregado a $CMDLINE"
else
    echo "consoleblank=0 ya estaba presente en $CMDLINE"
fi

# 3. Estabilidad de reloj SPI en config.txt
CONFIG="/boot/firmware/config.txt"
if [ ! -f "$CONFIG" ]; then CONFIG="/boot/config.txt"; fi

if ! grep -q "core_freq=400" "$CONFIG"; then
    echo "Fijando core_freq=400 y core_freq_min=400 en $CONFIG..."
    echo -e "\n# Estabilidad de reloj SPI para PaperTTY\ncore_freq=400\ncore_freq_min=400\n" >> "$CONFIG"
else
    echo "core_freq ya configurado en $CONFIG"
fi

# 4. Alias de limpieza instantánea en /home/q/.bashrc
if ! grep -q "papertty_clear_trigger" /home/q/.bashrc; then
    echo -e "\n# PaperTTY helper aliases\nalias clean='touch /tmp/papertty_clear_trigger'\nalias cls='touch /tmp/papertty_clear_trigger'\n" >> /home/q/.bashrc
    echo "Alias 'clean' y 'cls' agregados a /home/q/.bashrc"
fi

# 5. Optimización del servicio systemd
cat << 'EOF' > /etc/systemd/system/papertty-terminal.service
[Unit]
Description=PaperTTY Terminal for WeAct 3.7 e-Paper (Terminus 6x12 High-Performance)
After=local-fs.target
DefaultDependencies=no
After=basic.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/q/PaperTTY
Environment=PYTHONPATH=/home/q/PaperTTY
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/q/PaperTTY/venv/bin/python3 -m papertty.papertty --driver WeAct3in7_UC8253 terminal --vcsa /dev/vcsa1 --font /usr/share/fonts/truetype/terminus/TerminusTTF-4.46.0.ttf --size 12 --autofit --sleep 0.05 --cursor none
Restart=always
RestartSec=2

# Prioridad de CPU e I/O para latencia mínima
Nice=-10
IOSchedulingClass=best-effort
IOSchedulingPriority=2
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart papertty-terminal.service

echo "=== Optimizaciones aplicadas exitosamente ==="
