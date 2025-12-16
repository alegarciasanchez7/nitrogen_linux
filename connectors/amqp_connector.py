"""
Implementación de conector AMQP para RabbitMQ con Autenticación
"""
import pika
from .connector import Connector

class AmqpConnector(Connector):
    def __init__(self, name, template, 
                 host="localhost", port=5672, 
                 queue="nitrogen_queue", 
                 user="guest", password="guest", # Nuevos parámetros
                 on_message_callback=None):
        
        super().__init__(name, template, on_message_callback)
        self.host = host
        self.port = int(port)
        self.queue = queue
        self.user = user
        self.password = password
        
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.log(f"[{self.name}] Conectando a RabbitMQ en {self.host}:{self.port} ({self.user})...")
            
            # Credenciales
            credentials = pika.PlainCredentials(self.user, self.password)
            
            # Configuración de conexión completa
            params = pika.ConnectionParameters(
                host=self.host, 
                port=self.port,
                credentials=credentials
                # virtual_host='/'  # Se podría añadir si fuera necesario
            )
            
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # Declaramos la cola (durable=True es recomendado para persistencia)
            self.channel.queue_declare(queue=self.queue)
            
            self.log(f"[{self.name}] ¡Conexión RabbitMQ establecida! Cola: {self.queue}")
        except Exception as e:
            self.log(f"[{self.name}] ERROR RabbitMQ: {e}")

    def send(self):
        msg = self._process_template()
        
        # Reconexión automática
        if not self.connection or self.connection.is_closed:
            self.connect()

        if self.channel and self.channel.is_open:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue,
                    body=msg
                )
                self.log(f"[{self.name}] AMQP -> {self.queue}: {msg}")
            except Exception as e:
                self.log(f"[{self.name}] Error enviando mensaje: {e}")
                # Forzar reconexión en el siguiente intento
                try:
                    self.connection.close()
                except:
                    pass
        else:
            self.log(f"[{self.name}] ERROR: No hay conexión con RabbitMQ")