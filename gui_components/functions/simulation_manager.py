"""
Gestor de simulación - Inicia y detiene la simulación
"""
import threading
from nitrogen_linux import NitrogenEngine, Group
from connectors import MqttConnector, FileConnector, AmqpConnector


class SimulationManager:
    def __init__(self, conn_config, var_handlers, control_panel):
        self.conn_config = conn_config
        self.var_handlers = var_handlers
        self.control = control_panel
        
        self.engine = None
        self.engine_thread = None
        
        # Conectar botones
        self.control.btn_start.config(command=self.start_simulation)
        self.control.btn_stop.config(command=self.stop_simulation)
    
    def start_simulation(self):
        """Inicia la simulación"""
        if not self.var_handlers.added_variables:
            return
        
        # Obtener configuración
        config = self.conn_config.get_config()
        
        # Crear motor
        self.engine = NitrogenEngine(frequency_ms=config["frequency"])
        
        # Crear plantilla JSON
        json_parts = [
            f'"{v.name}": "{{{v.name}}}"' 
            for v in self.var_handlers.added_variables 
            if v is not None
        ]
        template = "{" + ", ".join(json_parts) + "}"
        
        # Crear conector según tipo
        connector = self._create_connector(config, template)
        
        # Añadir variables al conector
        for v in self.var_handlers.added_variables:
            if v is not None:
                connector.add_variable(v)
        
        # Crear grupo y añadir al motor
        grp = Group("Main")
        grp.add_connector(connector)
        self.engine.add_group(grp)
        
        # Iniciar en hilo separado
        self.engine_thread = threading.Thread(target=self.engine.start)
        self.engine_thread.daemon = True
        self.engine_thread.start()
        
        # Actualizar UI
        self.control.btn_start.config(state="disabled")
        self.control.btn_stop.config(state="normal")
    
    def _create_connector(self, config, template):
        """Crea el conector apropiado según la configuración"""
        conn_type = config["type"]
        options = config["options"]
        
        if conn_type == "MQTT":
            host = options["host"].get()
            topic = options["topic"].get()
            return MqttConnector(
                "MQTT_Client", 
                template, 
                host=host, 
                topic=topic, 
                on_message_callback=self.control.log
            )
        
        elif conn_type == "RabbitMQ":
            host = options["host"].get()
            queue = options["queue"].get()
            return AmqpConnector(
                "RabbitMQ", 
                template, 
                host=host, 
                queue=queue, 
                on_message_callback=self.control.log
            )
        
        else:  # Fichero
            path = options["filepath"].get()
            return FileConnector(
                "File_Logger", 
                template, 
                filepath=path, 
                on_message_callback=self.control.log
            )
    
    def stop_simulation(self):
        """Detiene la simulación"""
        if self.engine:
            self.engine.running = False
            self.control.btn_start.config(state="normal")
            self.control.btn_stop.config(state="disabled")
