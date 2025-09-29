import time
import board
import digitalio
import pwmio
import json 

#-----------Broker MQTT-----------#
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
# Configuración de RED
SSID = "Tu wifi"
PASSWORD = "Contraseña de tu wifi"
BROKER = "La IPv4 de la pc donde corre mosquitto. Win: ipconfig o Linux: ip addr"  
NOMBRE_EQUIPO = "Mason Mount "
DESCOVERY_TOPIC = "descubrir"
TOPIC = f"sensores/{NOMBRE_EQUIPO}"

print(f"Intentando conectar a {SSID}...")
try:
    wifi.radio.connect(SSID, PASSWORD)
    print(f"Conectado a {SSID}")
    print(f"Dirección IP: {wifi.radio.ipv4_address}")
except Exception as e:
    print(f"Error al conectar a WiFi: {e}")
    while True:
        pass 

# Configuración MQTT 
pool = socketpool.SocketPool(wifi.radio)

def connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT")
    client.publish(DESCOVERY_TOPIC, json.dumps({"equipo":NOMBRE_EQUIPO,"magnitudes": ["temperatura", "humedad"]}))

mqtt_client = MQTT.MQTT(
    broker=BROKER,
    port=1883,
    socket_pool=pool
)

mqtt_client.on_connect = connect
mqtt_client.connect()

# Usamos estas varaibles globales para controlar cada cuanto publicamos
LAST_PUB = 0
PUB_INTERVAL = 5  
def publish(calidad_buena: int, calidad_mala: int, total: int):
    global last_pub
    now = time.monotonic()
    
    if now - last_pub >= PUB_INTERVAL:
        try:
            calidad_buena_topic = f"{TOPIC}/[Prendas de calidad buena]" 
            mqtt_client.publish(calidad_buena_topic, str([calidad_buena]))
            
            calidad_mala_topic = f"{TOPIC}/[Prendas de calidad mala]" 
            mqtt_client.publish(calidad_mala_topic, str([calidad_mala]))
            
            total_topic = f"{TOPIC}/[Total de prendas inspeccionadas]" 
            mqtt_client.publish(total_topic, str([total]))  
            last_pub = now
          
        except Exception as e:
            print(f"Error publicando MQTT: {e}")
#-----------BrokerMQTT-----------#


'''
Componentes:
    - Micrófono KY-038
    - Motor paso a paso 28BYJ-48 con driver ULN2003
    - LED azul
    - Sensor infrarrojo KY-033
    - LED RGB (agregado)
    - Botón/pulsador (agregado)
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

    def mover_cinta_adelante(self, pasos=1):
        for _ in range(pasos):
            for paso in self.secuencia:
                self._paso_motor(paso)
                time.sleep(0.002)  # Ajusta velocidad (más chico = más rápido)

    def mover_cinta_atras(self, pasos=1):
        for _ in range(pasos):
            for paso in reversed(self.secuencia):
                self._paso_motor(paso)
                time.sleep(0.002)  # Ajusta velocidad (más chico = más rápido)

    def detener(self):
        """Detiene el motor apagando todas las bobinas"""
        for pin in self.in_pins:
            pin.value = False

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

class Boton:
    """Controla un botón"""
    def __init__(self, pin:board.Pin):
        """Inicializo el pin del botón"""
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.INPUT
        self.pin.pull = digitalio.Pull.UP  # Asumo que el botón conecta a GND cuando se presiona

    def presionar(self) -> bool:
        """Devuelve True si el botón está presionado"""
        return not self.pin.value  # El botón devuelve LOW cuando está presionado


class EstacionDeControl:
    """Clase principal que integra todos los componentes"""
    def __init__(self):
        self.microfono = Microfono(board.GP13)
        self.motor = MotorPasoPaso(pins=[board.GP18, board.GP19, board.GP20, board.GP21])
        self.led_azul = LedAzul(board.GP15)
        self.sensor_infrarrojo = SensorInfrarrojo(board.GP16)
        self.led_rgb = LedRGB(r=board.GP10, g=board.GP11, b=board.GP12)
        self.boton = Boton(board.GP14)

        self.calidad_buena= 0
        self.calidad_mala= 0
        
        # Estados posibles
        self.espera = 0
        self.deteccion = 1
        self.inspeccion = 2
    
        self.estado_actual = self.espera

    def _espera(self):
        """Fase de espera: cinta en movimiento, leds apagados."""
        # Cinta en movimiento
        self.motor.mover_cinta_adelante()
        self.led_azul.apagar()
        self.led_rgb.set_color(0, 0, 0)

        # Si detecta un objeto, pasa a la siguiente fase
        if self.sensor_infrarrojo.detectar():
            self.estado_actual = self.deteccion

    def _deteccion(self):
        """Fase de detección: el sensor infrarrojo detecta un objeto, se detiene la cinta, se prende el LED azul."""
        # Detener cinta, prender LED azul (inspección)
        self.led_azul.prender()
        self.motor.detener()
        
        # Pasar a la fase de inspección
        self.estado_actual = self.inspeccion
        
    def _inspeccion(self):
        """Fase de fin de inspección"""

        # Esperar a que se detecte sonido (ok) o se presione el botón (no ok)
        if self.boton.presionar():
            self._decision_calidad(ok=False)
            # Vuelve a la fase de espera
            self.estado_actual = self.espera
        elif self.microfono.escuchar():
            self._decision_calidad(ok=True)
            # Vuelve a la fase de espera
            self.estado_actual = self.espera

    def _decision_calidad(self, ok):
        """Fase de decisión de calidad"""
        # Si está ok, debería prender verde y avanzar la cinta
        if ok:
            self.calidad_buena += 1
            self.led_rgb.set_color(0, 255, 0)  # Verde
            self.led_azul.apagar()
            time.sleep(1)
            self.motor.mover_cinta_adelante(pasos=200)  # Avanza 200 pasos para no interferir con el sensor
            time.sleep(2)
        
        # Si no está ok, debería prender rojo, retroceder la cinta para sacar la prenda y luego avanzar nuevamente
        else:
            self.calidad_mala += 1
            self.led_rgb.set_color(255, 0, 0)  # Rojo
            self.led_azul.apagar()
            time.sleep(1)
            self.motor.mover_cinta_atras(pasos=300)  # Retrocede 300 pasos
            time.sleep(3)  # Espera 3 segundos para sacar la prenda
        
        publish(calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala, total=self.calidad_buena+self.calidad_mala )  #Llamada a la función publish para enviar los datos al broker MQTT
            
    def activar(self):
        """bucle infinito con el programa principal"""
        while True:
            if self.estado_actual == self.espera:
                self._espera()
            elif self.estado_actual == self.deteccion:
                self._deteccion()
            elif self.estado_actual == self.inspeccion:
                self._inspeccion()
        



estacion_de_control = EstacionDeControl()
estacion_de_control.activar()

 #Llamada a la función publish para enviar los datos al broker MQTT
