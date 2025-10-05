import time
import board
import digitalio
import pwmio
import json 
import supervisor


#-----------Broker MQTT-----------#
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
# Configuración de RED
SSID = "wfrre-Docentes"
PASSWORD = "20$tscFrre.24"
BROKER = "10.13.100.84"
NOMBRE_EQUIPO = "Mason_Mount"
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
    client.publish(DESCOVERY_TOPIC, json.dumps({"equipo":NOMBRE_EQUIPO,"magnitudes": ["prendas"]}))

mqtt_client = MQTT.MQTT(
    broker=BROKER,
    port=1883,
    socket_pool=pool
)

mqtt_client.on_connect = connect
mqtt_client.connect()
 
def publish(calidad_buena: int, calidad_mala: int):
    """Publica los datos en el broker MQTT"""
    
    try:
        payload = [{"label": "Bueno", "value": calidad_buena},
            {"label": "Malo", "value": calidad_mala},
            {"label": "Total", "value": calidad_buena + calidad_mala}]
        
        prendas_topic = f"{TOPIC}/prendas"
        mqtt_client.publish(prendas_topic,  json.dumps(payload)) 

        # unidades_ok = f"{TOPIC}/unidades_ok" 
        # mqtt_client.publish(unidades_ok, str(calidad_buena))
        
        # unidades_no_ok = f"{TOPIC}/unidades_no_ok" 
        # mqtt_client.publish(unidades_no_ok, str(calidad_mala))
        
        # total_unidades = f"{TOPIC}/total_unidades" 
        # mqtt_client.publish(total_unidades, str(total))

      
    except Exception as e:
        print(f"Error publicando MQTT: {e}")
#-----------BrokerMQTT-----------#


#---------------------Funciones para monitoreo por pantalla----------------------#
def limpiar_pantalla():
    """Limpia la pantalla usando secuencias de escape ANSI"""
    print('\033[2J\033[H', end='')

def imprimir_resultados(estado_actual:str, calidad_buena:int, calidad_mala:int):
    limpiar_pantalla()
    print('---------------------Monitoreo de calidad---------------------')
    print('Fase actual:', estado_actual)
    print('Prendas OK:', calidad_buena)
    print('Prendas NO OK:', calidad_mala)
    print('Total:', calidad_buena + calidad_mala)


#---------------------Clases de componentes----------------------#   
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
        # Variables de los componentes
        self.microfono = Microfono(board.GP13)
        self.motor = MotorPasoPaso(pins=[board.GP18, board.GP19, board.GP20, board.GP21])
        self.led_azul = LedAzul(board.GP15)
        self.sensor_infrarrojo = SensorInfrarrojo(board.GP16)
        self.led_rgb = LedRGB(r=board.GP10, g=board.GP11, b=board.GP12)
        self.boton = Boton(board.GP14)

        # Variables de control
        self.calidad_buena= 0
        self.calidad_mala= 0
        
        # Variables de estado
        self.espera = 'espera'
        self.deteccion = 'deteccion'
        self.inspeccion = 'inspeccion'
        self.salvaguarda_motor = 'salvaguarda del motor'
        self.estado_actual = self.espera

        # Variables de tiempo
        self.tiempo_inicio = time.monotonic()
        self.tiempo_actual = 0

    def _espera(self):
        """Fase de espera: cinta en movimiento, leds apagados."""
        # Cinta en movimiento
        self.motor.mover_cinta_adelante()
        self.led_azul.apagar()
        self.led_rgb.set_color(0, 0, 0)

        # Si detecta un objeto, pasa a la siguiente fase
        if self.sensor_infrarrojo.detectar():
            self.estado_actual = self.deteccion
            imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)

    def _deteccion(self):
        """Fase de detección: el sensor infrarrojo detecta un objeto, se detiene la cinta, se prende el LED azul."""
        # Detener cinta, prender LED azul (inspección)
        self.led_azul.prender()
        self.motor.detener()
        time.sleep(1)

        # Pasar a la fase de inspección
        self.estado_actual = self.inspeccion
        imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)

    def _inspeccion(self):
        """Fase de fin de inspección"""

        # Esperar a que se detecte sonido (ok) o se presione el botón (no ok)
        if self.boton.presionar():
            self._decision_calidad(ok=False)
            # Vuelve a la fase de espera
            self.estado_actual = self.espera
            self.tiempo_inicio = time.monotonic()  # Reinicia el temporizador al volver a la espera
            imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)
        elif self.microfono.escuchar():
            self._decision_calidad(ok=True)
            # Vuelve a la fase de espera
            self.estado_actual = self.espera
            self.tiempo_inicio = time.monotonic()  # Reinicia el temporizador al volver a la espera
            imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)

    def _decision_calidad(self, ok):
        """Fase de decisión de calidad"""
        # Si está ok, debería prender verde y avanzar la cinta
        if ok:
            self.calidad_buena += 1
            self.led_rgb.set_color(0, 255, 0)  # Verde
            self.led_azul.apagar()
            time.sleep(1)
            self.motor.mover_cinta_adelante(pasos=200)  # Avanza 200 pasos para no interferir con el sensor

        # Si no está ok, debería prender rojo, retroceder la cinta para sacar la prenda y luego avanzar nuevamente
        else:
            self.calidad_mala += 1
            self.led_rgb.set_color(255, 0, 0)  # Rojo
            self.led_azul.apagar()
            time.sleep(1)
            self.motor.mover_cinta_atras(pasos=300)  # Retrocede 300 pasos
            time.sleep(3)  # Espera 3 segundos para sacar la prenda

        publish(calidad_buena =self.calidad_buena, calidad_mala=self.calidad_mala)  #Llamada a la función publish para enviar los datos al broker MQTT
            
    def _salvaguarda_motor(self):
        """Fase de alerta por motor demasiado tiempo activo"""
        self.motor.detener()
        self.tiempo_actual = time.monotonic() - self.tiempo_inicio

        if self.tiempo_actual > 60: # 1 minuto de inactividad
            self.tiempo_inicio = time.monotonic()  # Reinicia el temporizador
            self.estado_actual = self.espera
            imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)
        
        if supervisor.runtime.serial_bytes_available:
            entrada = input().strip().upper()
            if entrada == "1":
                self.tiempo_inicio = time.monotonic()  # Reinicia el temporizador
                self.estado_actual = self.espera
                imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)

    def activar(self):
        """bucle infinito con el programa principal"""

        imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)
        while True:
            #---------------------Programa principal---------------------#
            if self.estado_actual == self.espera:
                self._espera()
            elif self.estado_actual == self.deteccion:
                self._deteccion()
            elif self.estado_actual == self.inspeccion:
                self._inspeccion()
            elif self.estado_actual == self.salvaguarda_motor:
                self._salvaguarda_motor()
            
            #---------------------Control de tiempo de motor activo---------------------#
            self.tiempo_actual = time.monotonic() - self.tiempo_inicio
            if (self.tiempo_actual > 60) and (self.estado_actual == self.espera):  # Si el motor está activo por más de 1 minuto sin recibir interacción
                self.tiempo_inicio = time.monotonic()  # Reinicia el temporizador
                self.estado_actual = self.salvaguarda_motor
                imprimir_resultados(estado_actual=self.estado_actual, calidad_buena=self.calidad_buena, calidad_mala=self.calidad_mala)
                print("---------------------¡ Alerta !---------------------")
                print("Motor detenido por inactividad.")
                print("\n¿Desea continuar de todas formas? (1-Sí / 2-No)")
                self._salvaguarda_motor()

estacion_de_control = EstacionDeControl()
estacion_de_control.activar()
