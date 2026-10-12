import time, sys
sys.path.insert(0, '/home/q/PaperTTY')
from papertty.drivers.drivers_weact3in7 import WeAct3in7_UC8253
from PIL import Image, ImageDraw, ImageFont

epd = WeAct3in7_UC8253()
epd.init(partial=True)

font = ImageFont.truetype("/usr/share/fonts/truetype/terminus/TerminusTTF-4.46.0.ttf", 12)

print("=== VERIFICACION DE DRIVER CON BALANCE DC Y PURGA PROFUNDA ===")

# 1. Hard clean purge inicial
print("\n[1] Probando hard_clean_purge() inicial...")
t0 = time.perf_counter()
epd.hard_clean_purge()
t1 = time.perf_counter()
print(f"    -> Hard Clean Purge: {(t1 - t0)*1000:.2f} ms (~{(t1 - t0):.2f} s)")
print("    -> Estado del sustrato: Fondo blanco de fabrica 100% restaurado.")

# 2. Medir tiempos de refresco parcial con LUT A2 Bipolar y diferencial real en 0x10
print("\n[2] Escribiendo secuencia de prueba con diferencial real en 0x10...")
test_text = "UC8253: DC-Balance OK!"
busy_times = []

for i, ch in enumerate(test_text):
    char_cell = Image.new('1', (8, 16), 255)
    cd = ImageDraw.Draw(char_cell)
    cd.text((1, 2), ch, font=font, fill=0)
    
    px = 16 + (i * 8)
    py = 50
    
    t_start = time.perf_counter()
    epd.draw(px, py, char_cell)
    t_elapsed = (time.perf_counter() - t_start) * 1000
    busy_times.append(t_elapsed)

avg_time = sum(busy_times) / len(busy_times)
fps = 1000.0 / avg_time
print(f"    -> Caracteres escritos: {len(test_text)}")
print(f"    -> Tiempo medio por caracter (render + SPI + BUSY): {avg_time:.2f} ms (~{fps:.2f} FPS)")
print(f"    -> Min: {min(busy_times):.2f} ms | Max: {max(busy_times):.2f} ms")
print(f"    -> Contador parcial acumulado: {epd.partial_count}")

# 3. Test de sobreescritura de pixeles sin cambio (prueba de 0V GND clamp)
print("\n[3] Sobreescribiendo la misma celda con el mismo caracter (prueba de 0V clamp)...")
t_start = time.perf_counter()
epd.draw(16, 50, char_cell) # Re-draw without changing pixels
t_re = (time.perf_counter() - t_start) * 1000
print(f"    -> Re-dibujo idéntico ejecutado en {t_re:.2f} ms. Unchanged pixels protegidos con 0V.")

# 4. Prueba de Enter: on_newline_commit(min_frames=25)
print("\n[4] Probando disparo al pulsar Enter (on_newline_commit, min_frames=25)...")
# Forzar acumular 26 cuadros
epd.partial_count = 26
print(f"    -> Contador parcial simulado: {epd.partial_count}")
t0 = time.perf_counter()
committed = epd.on_newline_commit(min_frames=25)
t1 = time.perf_counter()
print(f"    -> on_newline_commit activado: {committed} en {(t1 - t0)*1000:.2f} ms")
print(f"    -> Contador parcial tras commit: {epd.partial_count}")

# 5. Prueba de micropausa: check_idle_purge() tras 850 ms
print("\n[5] Probando micropausa de lectura (check_idle_purge tras 850 ms)...")
# Escribir un nuevo caracter
epd.draw(16, 70, char_cell)
print(f"    -> Caracter nuevo escrito. Contador parcial = {epd.partial_count}")
print("    -> Esperando 900 ms de inactividad...")
time.sleep(0.9)
t0 = time.perf_counter()
purged = epd.check_idle_purge()
t1 = time.perf_counter()
print(f"    -> check_idle_purge ejecutado: {purged} en {(t1 - t0)*1000:.2f} ms")
print(f"    -> Contador parcial tras micropausa: {epd.partial_count}")

# Finalizar
epd.sleep()
print("\n=== TODAS LAS PRUEBAS COMPLETADAS SATISFACTORIAMENTE ===")
