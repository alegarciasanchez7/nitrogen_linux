"""
Implementación de conexión MQTT
"""
import paho.mqtt.client as mqtt
from .connector import Connector

class MqttConnector(Connector):
    # AÑADIDO: on_message_callback=None al final
    def __init__(self, name, template, host="localhost", port=1883, topic="nitrogen/data", on_message_callback=None):
        # IMPORTANTE: Pasar on_message_callback al padre (Connector)
        super().__init__(name, template, on_message_callback)
        
        self.host = host
        self.port = port
        self.topic = topic
        
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.is_connected = False

    def connect(self):
        try:
            # CAMBIO: Usamos self.log
            self.log(f"[{self.name}] Conectando a MQTT {self.host}:{self.port}...")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start() 
            self.is_connected = True
            self.log(f"[{self.name}] ¡Conexión establecida!")
        except Exception as e:
            self.log(f"[{self.name}] Error conectando a MQTT: {e}")

    def send(self):
        message = self._process_template()
        
        if not self.is_connected:
            self.connect()

        if self.is_connected:
            info = self.client.publish(self.topic, message)
            info.wait_for_publish()
            # CAMBIO: Usamos self.log para que salga en la GUI
            self.log(f"[{self.name}] MQTT -> {self.topic}: {message}")
        else:
            self.log(f"[{self.name}] ERROR: No se pudo enviar (Sin conexión)")