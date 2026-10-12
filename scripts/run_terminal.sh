#!/bin/bash
# Script para iniciar la terminal interactiva de PaperTTY en la WeAct 3.7" UC8253
# Configurada con fuente Terminus 6x12 pixel-perfect y refresco A2 calibrado

cd /home/q/PaperTTY
export PYTHONPATH=/home/q/PaperTTY

echo "Iniciando terminal PaperTTY en WeAct 3.7 (Terminus 6x12, 20 MHz, ~6.2 FPS)..."
echo "Presiona Ctrl+C para salir."

sudo /home/q/PaperTTY/venv/bin/python3 -m papertty.papertty \
    --driver WeAct3in7_UC8253 \
    terminal \
    --vcsa /dev/vcsa1 \
    --font /usr/share/fonts/truetype/terminus/TerminusTTF-4.46.0.ttf \
    --size 12 \
    --autofit \
    --sleep 0.05 \
    --cursor none
