"""
Implementación de conector AMQP para RabbitMQ
"""
import pika
from .connector import Connector

class AmqpConnector(Connector):
    def __init__(self, name, template, host="localhost", port=5672, 
                 queue="nitrogen_queue", on_message_callback=None):
        super().__init__(name, template, on_message_callback)
        self.host = host
        self.port = int(port)
        self.queue = queue # En AMQP simple usamos la cola como routing_key
        
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.log(f"[{self.name}] Conectando a RabbitMQ en {self.host}:{self.port}...")
            
            # Configuración básica de conexión (Guest/Guest por defecto)
            params = pika.ConnectionParameters(host=self.host, port=self.port)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # IMPORTANTE: Declaramos la cola por si no existe
            self.channel.queue_declare(queue=self.queue)
            
            self.log(f"[{self.name}] ¡Conexión RabbitMQ establecida! Cola: {self.queue}")
        except Exception as e:
            self.log(f"[{self.name}] ERROR RabbitMQ: {e}")

    def send(self):
        msg = self._process_template()
        
        # Reconexión automática si se cae
        if not self.connection or self.connection.is_closed:
            self.connect()

        if self.channel and self.channel.is_open:
            try:
                # Publicamos en el intercambio por defecto (exchange="")
                # usando el nombre de la cola como routing_key
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue,
                    body=msg
                )
                self.log(f"[{self.name}] AMQP -> {self.queue}: {msg}")
            except Exception as e:
                self.log(f"[{self.name}] Error enviando mensaje: {e}")
        else:
            self.log(f"[{self.name}] ERROR: No hay conexión con RabbitMQ")