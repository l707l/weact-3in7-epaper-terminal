# WeAct 3.7" E-Paper Terminal — Raspberry Pi (UC8253)

> **Terminal interactiva de alto rendimiento en tinta electrónica para Raspberry Pi con controlador UltraChip UC8253 y PaperTTY.**

[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%203B%2B%20%2F%204B%20%2F%20Zero%202W-red.svg)](https://www.raspberrypi.com/)
[![Display](https://img.shields.io/badge/Display-WeAct%203.7%22%20(GDEY037T03)-blue.svg)](https://github.com/WeActStudio/WeActStudio.EpaperModule)
[![Controller](https://img.shields.io/badge/Controller-UltraChip%20UC8253-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ Características Principales

* **Frecuencia SPI Elevada:** Bus SPI a **20.0 MHz** con transferencias DMA directas vía `spidev` y `spi_bcm2835`.
* **Comparador Diferencial Real en Hardware:**
  * Registro `0x10` recibe los bytes previos reales del recorte (`old_crop_bytes`).
  * Registro `0x13` recibe los nuevos bytes (`new_crop_bytes`).
  * Los píxeles que no cambian (Negro $\to$ Negro o Blanco $\to$ Blanco) reciben $0\text{V}$ reales en el silicio, eliminando caracteres alternados en gris.
* **Forma de Onda Fast A2 Bipolar:**
  * Fase de contra-pulso de ecualización para cancelar la carga residual ($\int V dt \approx 0$).
  * Fase de asentamiento directo para máxima densidad óptica en pigmentos negros.
* **Bounding Box Atómico de Carácter:**
  * Recorte de ventana parcial estricto de **$16 \times 6$ píxeles** (solo 12 bytes transferidos por tecla).
  * Refresco focalizado sin tocar el 99.8% restante de la pantalla.
* **Ergonomía y Cero Parpadeo:**
  * **0 parpadeos** durante digitación continua en la misma línea.
  * Detección de desplazamiento de terminal (`is_scroll=True`): comandos de texto (`ls`, `cat`) y saltos con `Enter` fluyen en modo parcial rápido.
  * Detección inteligente de herramientas TUI a pantalla completa (`btop`, `htop`, `top`, `fastfetch`) para asentamiento global limpio.
  * Purga profunda dieléctrica (**Hard Clean Purge**) con forma de onda OTP tras **50.0 segundos** de inactividad o al invocar `clear`/`clean`.
* **Tipografía Pixel-Perfect:**
  * Fuente bitmap nativa **Terminus 6×12** (`--size 12`, `fontmode='1'`).
  * Área de trabajo en apaisado ($416 \times 240$): **69 columnas $\times$ 19 filas**.

---

## 🔌 Conexiones de Hardware (Pinout)

Conexión de la pantalla **WeAct Studio 3.7" E-Paper** a la cabecera GPIO de 40 pines de la Raspberry Pi:

| Señal Módulo | Función | Pin Físico RPi | Pin BCM (GPIO) | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **3.3V (VCC)** | Alimentación | Pin 1 | 3.3V Power | Alimentación lógica y analógica (**NO usar 5V**) |
| **GND** | Tierra | Pin 6 | GND | Referencia común |
| **DIN (MOSI)** | Datos SPI | Pin 19 | GPIO 10 (SPI0_MOSI) | Datos serie maestro a esclavo |
| **CLK (SCK)** | Reloj SPI | Pin 23 | GPIO 11 (SPI0_SCLK) | Señal de reloj SPI (hasta 20 MHz) |
| **CS** | Chip Select | Pin 24 | GPIO 8 (SPI0_CE0) | Selección de chip (activo en BAJO) |
| **DC** | Datos/Comando | Pin 22 | GPIO 25 | Control de modo: BAJO = Cmd, ALTO = Data |
| **RST** | Reset Hardware | Pin 11 | GPIO 17 | Reset del controlador UC8253 |
| **BUSY** | Estado del Panel | Pin 18 | GPIO 24 | Detección de motor analógico (**0 = Ocupado**) |

---

## 📁 Estructura del Repositorio

```text
weact-3in7-epaper-terminal/
├── drivers/
│   ├── drivers_weact3in7.py    # Driver de producción para WeAct 3.7" (UC8253)
│   └── drivers_base.py         # Clase base con parches para lgpio/gpiozero y 20MHz SPI
├── systemd/
│   └── papertty-terminal.service # Definición del servicio systemd para inicio automático
├── scripts/
│   ├── install.sh              # Script de instalación y configuración automática
│   ├── run_terminal.sh         # Script para ejecución manual interactiva
│   └── trigger_clean.sh        # Disparador manual de purga profunda
├── tests/
│   ├── type_keys.py            # Inyector de teclado a bajo nivel (/dev/tty1)
│   ├── test_dc_balance.py      # Medición de balance DC e inmunidad a polarización
│   └── benchmark.py            # Medición de tasas de transferencia y tiempos de ciclo
├── docs/
│   └── INFORME_TECNICO.md      # Informe técnico exhaustivo de ingeniería inversa
├── papertty.py                 # Motor principal de PaperTTY optimizado
├── requirements.txt            # Dependencias Python
├── .gitignore
└── README.md
```

---

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/l707l/weact-3in7-epaper-terminal.git
cd weact-3in7-epaper-terminal
```

### 2. Ejecutar el Instalador Automático
```bash
chmod +x scripts/install.sh scripts/trigger_clean.sh scripts/run_terminal.sh
./scripts/install.sh
```

El script se encargará de:
1. Instalar dependencias del sistema (`python3-pil`, `python3-spidev`, `python3-gpiozero`, `fonts-terminus`).
2. Habilitar SPI por hardware en `/boot/firmware/config.txt`.
3. Configurar el entorno virtual e instalar módulos Python.
4. Instalar e iniciar el servicio `papertty-terminal.service`.

---

## ⚙️ Uso y Comandos Útiles

### Estado del Servicio
```bash
sudo systemctl status papertty-terminal.service
```

### Monitoreo de Registros en Tiempo Real
```bash
journalctl -u papertty-terminal.service -f
```

### Forzar Purga Profunda Inmediata
Si deseas limpiar el panel manualmente en cualquier momento:
```bash
./scripts/trigger_clean.sh
# O simplemente:
touch /tmp/papertty_clear_trigger
```

### Simular Digitación por Terminal
```bash
python3 tests/type_keys.py "ls -la"
```

---

## 📊 Métricas de Rendimiento

| Métrica | Valor Obtenido | Observaciones |
| :--- | :--- | :--- |
| **Velocidad de Bus SPI** | 20.0 MHz | Transferencias vía DMA por hardware |
| **Tiempo de Ciclo por Carácter** | ~145–165 ms | Asentamiento completo de partículas |
| **Tasa de Refresco Máxima** | ~6.1–6.5 FPS | Modo parcial continuo en línea |
| **Bytes por Pulsación de Tecla** | 12 bytes | Ventana atómica de 16×6 píxeles |
| **Resolución Apaisada** | 69 cols × 19 filas | Fuente Terminus 6×12 sin interpolación |
| **Purga por Inactividad** | 50.0 segundos | Drenaje dieléctrico profundo con forma de onda OTP |

---

## 📚 Documentación Técnica Detallada

Para consultar el análisis exhaustivo de hardware, arquitectura del silicio UC8253, diagramas de transición de fase, mapas de memoria y comparador diferencial, revisa el archivo [docs/INFORME_TECNICO.md](docs/INFORME_TECNICO.md).

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.
