import time
import board
import digitalio


class MotorPasoPaso:
    """Controla un motor paso a paso 28BYJ-48 usando un conversor de niveles"""
    pass

class Led:
    """Controla el LED"""
    pass






































# Pines conectados al conversor de niveles (lado LV)
pins = [board.GP18, board.GP19, board.GP20, board.GP21]

# Configurar pines como salida digital
in_pins = []
for p in pins:
    pin = digitalio.DigitalInOut(p)
    pin.direction = digitalio.Direction.OUTPUT
    in_pins.append(pin)

# Secuencia del motor (media fase / half-step)
secuencia = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def paso_motor(paso):
    """Escribe un paso en los pines"""
    for i in range(4):
        in_pins[i].value = bool(paso[i])

# Prueba: hacer girar 1 vuelta completa
# (28BYJ-48 suele necesitar 512 pasos por vuelta en half-step)
while True:
    for paso in secuencia:
        paso_motor(paso)
        time.sleep(0.002)  # Ajusta velocidad (más chico = más rápido)
