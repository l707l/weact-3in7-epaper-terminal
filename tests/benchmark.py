import time
import sys
sys.path.insert(0, '/home/q/PaperTTY')
from PIL import Image, ImageDraw
from papertty.drivers.drivers_weact3in7 import WeAct3in7_UC8253

epd = WeAct3in7_UC8253()
epd.init(partial=True)

# 1. Benchmark Partial Window (1 keystroke character, 12 bytes payload)
sub = Image.new('1', (8, 12), 0)
x, y = 80, 50

render_times = []
spi_times = []
busy_times = []
total_times = []

for i in range(10):
    t_start = time.perf_counter()

    t0 = time.perf_counter()
    w, h = sub.size
    x1 = int(x) & ~7
    x2 = (int(x) + w + 7) & ~7
    w1 = x2 - x1
    y1 = int(y)
    y2 = int(y) + h
    h1 = y2 - y1

    epd.canvas.paste(sub, (x, y))
    crop = epd.canvas.crop((x1, y1, x2, y2))
    crop_bytes = list(crop.tobytes())
    white_bytes = [0xFF] * len(crop_bytes)
    t_render = time.perf_counter() - t0

    t1 = time.perf_counter()
    xe = x2 - 1
    ye = y2 - 1
    epd.send_command(0x91)
    epd.send_command(0x90)
    epd.send_data(x1 & 0xFF)
    epd.send_data(xe & 0xFF)
    epd.send_data((y1 >> 8) & 0xFF)
    epd.send_data(y1 & 0xFF)
    epd.send_data((ye >> 8) & 0xFF)
    epd.send_data(ye & 0xFF)
    epd.send_data(0x01)

    epd.send_command(0x10)
    epd.send_data_multi(white_bytes)

    epd.send_command(0x13)
    epd.send_data_multi(crop_bytes)

    epd.send_command(0xE0)
    epd.send_data(0x02)
    epd.send_command(0xE5)
    epd.send_data(0x6E)
    epd.send_command(0x50)
    epd.send_data(0xD7)

    epd.send_command(0x12)
    t_spi = time.perf_counter() - t1

    t2 = time.perf_counter()
    epd.wait_until_idle()
    t_busy = time.perf_counter() - t2

    epd.send_command(0x92)

    t_tot = time.perf_counter() - t_start

    render_times.append(t_render * 1000)
    spi_times.append(t_spi * 1000)
    busy_times.append(t_busy * 1000)
    total_times.append(t_tot * 1000)

    x += 8
    if x > 200:
        x = 80
        y += 16

avg_render = sum(render_times) / len(render_times)
avg_spi = sum(spi_times) / len(spi_times)
avg_busy = sum(busy_times) / len(busy_times)
avg_total = sum(total_times) / len(total_times)
fps = 1000.0 / avg_total

print("=== NUEVAS METRICAS MEDIDAS EN HARDWARE (SPI 20 MHz + Polling 200us) ===")
print(f"1. Renderizado local (PIL):       {avg_render:.3f} ms")
print(f"2. Transferencia bus SPI (20MHz): {avg_spi:.3f} ms")
print(f"3. Espera pin BUSY (200us poll):  {avg_busy:.3f} ms")
print(f"4. Tiempo total ciclo por cuadro: {avg_total:.3f} ms")
print(f"5. FPS efectivos en ventana:      {fps:.2f} FPS")

# Benchmark Full Refresh a 20MHz
t0 = time.perf_counter()
raw_bytes = list(epd.canvas.tobytes())
t_render_full = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
epd.send_command(0x10)
epd.send_data_multi(raw_bytes)
epd.send_command(0x13)
epd.send_data_multi(raw_bytes)
epd.send_command(0x50)
epd.send_data(0xD7)
epd.send_command(0x12)
t_spi_full = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
epd.wait_until_idle()
t_busy_full = (time.perf_counter() - t0) * 1000

t_tot_full = t_render_full + t_spi_full + t_busy_full
print("\n=== METRICAS FULL FRAME REFRESH (24,960 Bytes @ 20 MHz) ===")
print(f"1. Render local:                  {t_render_full:.3f} ms")
print(f"2. Transferencia bus SPI (20MHz): {t_spi_full:.3f} ms")
print(f"3. Espera pin BUSY:               {t_busy_full:.3f} ms")
print(f"4. Tiempo total ciclo completo:   {t_tot_full:.3f} ms")
print(f"5. FPS efectivos full refresh:    {1000.0 / t_tot_full:.2f} FPS")
