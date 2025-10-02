# 🏭 Estación de Control de Calidad Textil

Sistema automatizado de control de calidad para líneas de producción textil implementado con **CircuitPython** y **Raspberry Pi Pico**.

## 📋 Descripción del Proyecto

Este proyecto simula una estación de control de calidad en una línea de producción textil, específicamente para la confección de remeras. El sistema combina detección automática con intervención humana para verificar costuras y defectos visibles antes del empaquetado final.

## 🔧 Componentes Utilizados

- **Microcontrolador**: Raspberry Pi Pico
- **Micrófono**: KY-038 (detección de chasquidos del operario)
- **Motor**: Paso a paso 28BYJ-48 con driver ULN2003
- **Sensor**: Infrarrojo KY-033 (detección de presencia)
- **LEDs**: 
  - LED azul (luz de inspección)
  - LED RGB (indicador de resultado)
- **Botón**: Pulsador para rechazo de calidad
- **Batería de 9 V**: Fuente de alimentación externa para el motor

## 🔌 Conexiones

| Componente | Pin GPIO | Descripción |
|------------|----------|-------------|
| Micrófono KY-038 | GP13 | Señal digital de detección de sonido |
| Motor (IN1-IN4) | GP18-GP21 | Control del motor paso a paso |
| LED Azul | GP15 | Indicador de luz de inspección |
| Sensor Infrarrojo | GP16 | Detección de presencia de objeto |
| LED RGB (R,G,B) | GP10,GP11,GP12 | Indicador de resultado de calidad |
| Botón | GP14 | Señal de rechazo de calidad |
| Batería 9 V | COM ULN2003 + VCC motor | Alimentación del motor paso a paso |

## 🎯 Fases de Funcionamiento

### 1️⃣ **Espera del Objeto**
- 🔄 Motor mantiene la cinta en movimiento continuo
- 🔵 LED azul apagado
- 🌈 LED RGB inactivo
- 👁️ Sensor infrarrojo monitoreando

### 2️⃣ **Detección de la Prenda**
- 🛑 Motor se detiene automáticamente
- 🔵 LED azul se enciende (luz de inspección)
- ⏳ Sistema espera intervención del operario

### 3️⃣ **Fin de Inspección**
El operario tiene dos opciones:
- 🔊 **Chasquido** (micrófono) → Calidad suficiente
- 🔴 **Botón** → Calidad insuficiente

### 4️⃣ **Decisión de Calidad**

#### ✅ **Calidad OK** (Chasquido detectado)
- 🟢 LED RGB se ilumina en **verde**
- ➡️ Motor avanza enviando la prenda a la siguiente estación
- 🔄 Retorna automáticamente al estado de espera

#### ❌ **Calidad No OK** (Botón presionado)
- 🔴 LED RGB se ilumina en **rojo**
- ⬅️ Motor retrocede enviando la prenda a reproceso
- 🔄 Retorna automáticamente al estado de espera

## 🏗️ Arquitectura del Sistema

El sistema utiliza una **máquina de estados** con los siguientes estados:

```
ESPERA_OBJETO → DETECCION_PRENDA → FIN_INSPECCION → DECISION_CALIDAD
                                                            ↓
ESPERA_OBJETO ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←← RETROCESO (si calidad No OK)
```

## 📊 Estadísticas de Producción

El sistema contabiliza automáticamente:
- ✅ Prendas aprobadas (calidad_buena)
- ❌ Prendas rechazadas (calidad_mala)
- 📦 Total de prendas inspeccionadas
Estos valores se muestran en la consola serial y también pueden enviarse vía **MQTT** a un broker remoto.

## 🌐 Integración con MQTT

Además del control local, el sistema cuenta con un módulo de red implementado en broker.py, que permite:
- Conexión a una red WiFi.
- Publicación periódica de estadísticas en un broker MQTT.
- Descubrimiento automático del dispositivo en la red.

## 📁 Estructura del Proyecto

```
TEPLA_UTN/
├── microcontrolador.py    # Implementación completa con máquina de estados
├── broker.py              # Cliente MQTT para reporte de estadísticas
├── code.py               # Versión de desarrollo/pruebas
└── README.md            # Este archivo
```

## 🚀 Instalación y Uso

### Prerrequisitos
- Raspberry Pi Pico con CircuitPython instalado
- Todos los componentes conectados según el diagrama de conexiones

### Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/EnzoCoschiza/TEPLA_UTN.git
   ```

2. Copia `microcontrolador.py` a tu Raspberry Pi Pico como `code.py`

3. Reinicia el Pico para ejecutar el programa

### Uso
1. El sistema iniciará automáticamente en modo **ESPERA_OBJETO**
2. Coloca una prenda en la cinta transportadora
3. Cuando el sensor detecte la prenda, el sistema se detendrá
4. Realiza la inspección visual de calidad
5. Comunica el resultado:
   - **Chasquido** para aprobar
   - **Botón** para rechazar
6. El sistema procesará automáticamente la decisión

## 🔍 Monitoreo del Sistema

El sistema incluye mensajes informativos en la consola:
- `"Prenda detectada - Motor detenido - Luz de inspección activada"`
- `"Chasquido detectado - Calidad OK"`
- `"Botón presionado - Calidad No OK"`
- `"LED verde - Enviando a siguiente estación"`
- `"LED rojo - Enviando a reproceso"`

## ⚙️ Personalización

### Ajuste de Velocidad del Motor
Modifica el valor `time.sleep()` en los métodos del motor:
```python
time.sleep(0.002)  # Menor valor = mayor velocidad
```

### Tiempo de Detección de Sonido
Ajusta la sensibilidad del micrófono modificando los delays en la clase `Microfono`.

### Número de Pasos para Avance/Retroceso
Modifica las variables `pasos_avance` y `pasos_retroceso` en `_decision_calidad()` y `_retroceso()`.


*Desarrollado como parte del programa académico de Tecnologías para la Automatización - UTN*

## 👥 Integrantes del Grupo

- Fidanza, Felipe
- Rodríguez Scornik, Matías
- Coschiza, Enzo
- Jerez, Fabricio
- Suarez, Tomás