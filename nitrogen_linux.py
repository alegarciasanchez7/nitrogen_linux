import time
from datetime import datetime
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable
from connectors import Connector, MqttConnector

# --- CLASE GRUPO (Simulando Sección 3.1 - Panel Central) ---

class Group:
    """Agrupa conectores """
    def __init__(self, name):
        self.name = name
        self.connectors = []

    def add_connector(self, connector):
        self.connectors.append(connector)

    def run_cycle(self):
        """Ejecuta un ciclo de envío para todos sus conectores"""
        for conn in self.connectors:
            conn.send()

# --- MOTOR PRINCIPAL (Simulando Configuración Global) ---

class NitrogenEngine:
    def __init__(self, frequency_ms=1000):
        self.frequency_ms = frequency_ms # 
        self.groups = []
        self.running = False

    def add_group(self, group):
        self.groups.append(group)

    def start(self):
        self.running = True
        print(f"--- Iniciando nITROGEN (Linux) - Freq: {self.frequency_ms}ms ---")
        try:
            while self.running:
                for group in self.groups:
                    group.run_cycle()
                
                # Control de frecuencia [cite: 118]
                time.sleep(self.frequency_ms / 1000.0)
        except KeyboardInterrupt:
            print("\nDeteniendo simulación...")

# --- EJEMPLO DE USO CON MQTT ---

if __name__ == "__main__":
    engine = NitrogenEngine(frequency_ms=2000) # 2 segundos por envío

    # 1. Definir Variables
    temp = NumericVariable("Temp", 20, 25, strategy="random")
    humedad = NumericVariable("Humedad", 40, 60, strategy="random")
    estado = ListVariable("Estado", ["ACTIVO", "ESPERA"], strategy="random")
    
    # Variable de fecha para timestamp
    reloj = DateVariable("Ts", strategy="now", date_format="%H:%M:%S")

    # 2. Configurar Conector MQTT
    # Usaremos el broker público de Eclipse para pruebas: test.mosquitto.org
    # Topic: nitrogen/linux/prueba (Puedes cambiarlo para que sea único)
    
    plantilla_json = '{"ts": "{Ts}", "sensor": "LinuxBox", "temp": {Temp}, "hum": {Humedad}, "st": "{Estado}"}'
    
    # Instanciamos el MqttConnector en lugar del Connector base
    mqtt_conn = MqttConnector("Salida_Nube", plantilla_json, 
                              host="test.mosquitto.org", 
                              port=1883, 
                              topic="nitrogen/linux/prueba")

    # Añadimos variables al conector
    mqtt_conn.add_variable(temp)
    mqtt_conn.add_variable(humedad)
    mqtt_conn.add_variable(estado)
    mqtt_conn.add_variable(reloj)

    # 3. Crear Grupo y Arrancar
    grupo = Group("Planta_IoT")
    grupo.add_connector(mqtt_conn)

    engine.add_group(grupo)
    
    print("Consejo: Para ver los mensajes, puedes usar un cliente web MQTT")
    print("o instalar 'mosquitto-clients' y ejecutar: mosquitto_sub -h test.mosquitto.org -t nitrogen/linux/prueba")
    print("-" * 60)
    
    engine.start()