import time
import board
import digitalio


'''
Componentes:
    - Micrófono KY-038
    - Motor paso a paso 28BYJ-48 con driver ULN2003
    - LED azul
    - Conversor de niveles (5V a 3.3V)
    - Sensor infrarrojo KY-033
    - LED RGB (agregado)
'''

class Microfono:
    """Controla el micrófono KY-038"""
    def __init__(self, pin : board.Pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT


class MotorPasoPaso:
    """Controla el motor paso a paso 28BYJ-48 usando un conversor de niveles"""
    pass


class LedAzul:
    """Controla el LED"""
    def __init__(self, pin : board.Pin):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT


class SensorInfrarrojo:
    """Controla el sensor infrarrojo KY-033"""
    pass


class LedRGB:
    """Controla el LED RGB"""
    pass


class EstacionDeControl:
    """Clase principal que integra todos los componentes"""
    def __init__(self):
        self.microfono = Microfono()
        self.motor = MotorPasoPaso()
        self.led_azul = LedAzul()
        self.sensor_infrarrojo = SensorInfrarrojo()
        self.led_rgb = LedRGB()



































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
