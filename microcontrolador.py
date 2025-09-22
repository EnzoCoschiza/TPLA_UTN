import time
import board
import digitalio
import pwmio


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
    def __init__(self, pin:board.Pin):
        """Inicializo el pin del micrófono"""
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT

    def escuchar(self) -> bool:
        """Devuelve True si detecta sonido"""
        return self.pin.value

class MotorPasoPaso:
    """Controla el motor paso a paso 28BYJ-48 usando un conversor de niveles"""
    def __init__(self, pins:list):
        """Inicializo los pines del motor y la secuencia que va a seguir"""
        # Configurar pines como salida digital
        self.in_pins = []
        for p in pins:
            pin = digitalio.DigitalInOut(p)
            pin.direction = digitalio.Direction.OUTPUT
            self.in_pins.append(pin)

        # Secuencia del motor (media fase / half-step)
        self.secuencia = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]
    def _paso_motor(self, paso):
        """Escribe un paso en los pines"""
        for i in range(4):
            self.in_pins[i].value = bool(paso[i])

    def mover_cinta_adelante(self):
        for paso in self.secuencia:
            self._paso_motor(paso)
            time.sleep(0.002)  # Ajusta velocidad (más chico = más rápido)
    
    def mover_cinta_atras(self):
        for paso in reversed(self.secuencia):
            self._paso_motor(paso)
            time.sleep(0.002)  # Ajusta velocidad (más chico = más rápido)

class LedAzul:
    """Controla el LED"""
    def __init__(self, pin:board.Pin):
        """Inicializo el pin del LED azul"""
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT

    def prender(self):
        self.pin.value = True

    def apagar(self):
        self.pin.value = False

class SensorInfrarrojo:
    """Controla el sensor infrarrojo KY-033"""
    def __init__(self, pin:board.Pin):
        """Inicializo el pin del sensor infrarrojo"""
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT

    def detectar(self) -> bool:
        """Devuelve True si detecta un objeto"""
        return not self.pin.value  # El sensor devuelve LOW cuando detecta un objeto


class LedRGB:
    """Controla el LED RGB"""
    def __init__(self, r:board.Pin, g:board.Pin, b:board.Pin):
        """Inicializo los pines del RGB"""
        self.r = pwmio.PWMOut(r, frequency=5000, duty_cycle=0)
        self.g = pwmio.PWMOut(g, frequency=5000, duty_cycle=0)
        self.b = pwmio.PWMOut(b, frequency=5000, duty_cycle=0)

    def set_color(self, r:int, g:int, b:int):
        """Establece el color del LED RGB
        r, g, b: valores entre 0 y 255
        """
        self.r.duty_cycle = int((r / 255) * 65535)
        self.g.duty_cycle = int((g / 255) * 65535)
        self.b.duty_cycle = int((b / 255) * 65535)


class EstacionDeControl:
    """Clase principal que integra todos los componentes"""
    def __init__(self):
        self.microfono = Microfono(board.GP13)
        self.motor = MotorPasoPaso(pins=[board.GP18, board.GP19, board.GP20, board.GP21])
        self.led_azul = LedAzul(board.GP15)
        self.sensor_infrarrojo = SensorInfrarrojo(board.GP16)
        self.led_rgb = LedRGB(r=board.GP10, g=board.GP11, b=board.GP12)

    def activar(self):
        """bucle infinito con el programa principal"""
        while True:
            self.motor.mover_cinta_adelante()


estacion_de_control = EstacionDeControl()
estacion_de_control.activar()



'''
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
'''