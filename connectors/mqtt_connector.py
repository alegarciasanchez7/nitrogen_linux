"""
Implementación de conexión MQTT
"""
import paho.mqtt.client as mqtt
from .connector import Connector

class MqttConnector(Connector):
    def __init__(self, name, template, host="localhost", port=1883, topic="nitrogen/data"):
        super().__init__(name, template)
        self.host = host
        self.port = port
        self.topic = topic
        
        # Configuración del cliente MQTT
        # Usamos protocol=mqtt.MQTTv311 para máxima compatibilidad
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.is_connected = False

    def connect(self):
        try:
            print(f"[{self.name}] Conectando a MQTT {self.host}:{self.port}...")
            self.client.connect(self.host, self.port, 60)
            
            # loop_start inicia un hilo en segundo plano para gestionar la red automáticamente
            self.client.loop_start() 
            self.is_connected = True
            print(f"[{self.name}] ¡Conexión establecida!")
        except Exception as e:
            print(f"[{self.name}] Error conectando a MQTT: {e}")

    def send(self):
        # Generamos el mensaje procesando las variables
        message = self._process_template()
        
        # Conexión "Lazy": conectamos solo cuando vamos a enviar el primer dato
        if not self.is_connected:
            self.connect()

        if self.is_connected:
            # Publicamos el mensaje en el topic configurado [cite: 171]
            info = self.client.publish(self.topic, message)
            info.wait_for_publish() # Opcional: esperar confirmación de envío
            print(f"[{self.name}] MQTT -> {self.topic}: {message}")
        else:
            print(f"[{self.name}] ERROR: No se pudo enviar (Sin conexión)")