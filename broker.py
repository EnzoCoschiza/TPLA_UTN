import time
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Configuración de RED
SSID = "Tu wifi"
PASSWORD = "Contraseña de tu wifi"
BROKER = "La IPv4 de la pc donde corre mosquitto. Win: ipconfig o Linux: ip addr"  
NOMBRE_EQUIPO = "relay"
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
def publish():
    global last_pub
    now = time.monotonic()
   
    if now - last_pub >= PUB_INTERVAL:
        try:
            temp_topic = f"{TOPIC}/[una_magnitud]" 
            mqtt_client.publish(temp_topic, str([var_de_una_magnitud]))
            
            hum_topic = f"{TOPIC}/[otra magnitud]" 
            mqtt_client.publish(hum_topic, str([var_de_otra_magnitud]))
            
            last_pub = now
          
        except Exception as e:
            print(f"Error publicando MQTT: {e}")
