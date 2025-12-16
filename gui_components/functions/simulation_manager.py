import threading
from tkinter import messagebox
from core import NitrogenEngine, Group
from connectors import MqttConnector, FileConnector, AmqpConnector
# Importamos los tipos para la lógica de comillas
from variables_type import NumericVariable, BooleanVariable 

class SimulationManager:
    def __init__(self, conn_config, var_handlers, control_panel):
        self.conn_config = conn_config
        self.var_handlers = var_handlers
        self.control = control_panel
        self.events_source = None 
        
        self.engine = None
        self.engine_thread = None
        
        self.control.btn_start.config(command=self.start_simulation)
        self.control.btn_stop.config(command=self.stop_simulation)
    
    def start_simulation(self):
        if not self.events_source or not self.events_source.events:
            messagebox.showwarning("Aviso", "No hay eventos definidos para simular.")
            return
        
        active_events = [e for e in self.events_source.events if e.variables]
        if not active_events:
            messagebox.showwarning("Aviso", "Los eventos definidos no tienen variables.")
            return

        config = self.conn_config.get_config()
        self.engine = NitrogenEngine()
        
        for evt in active_events:
            # --- CONSTRUCCIÓN INTELIGENTE DEL JSON ---
            json_parts = []
            
            # 1. EventTypeName
            json_parts.append(f'"EventTypeName": "{evt.name}"')
            
            # 2. Variables
            for v in evt.variables:
                # CASO A: Numéricos -> SIN comillas (ej: "edad": 25)
                if isinstance(v, NumericVariable):
                    part = f'"{v.name}": {{{v.name}}}'
                
                # CASO B: Booleanos -> SIN comillas (ej: "activo": True)
                # (Aquí es donde usamos la importación que faltaba)
                elif isinstance(v, BooleanVariable):
                    part = f'"{v.name}": {{{v.name}}}'
                
                # CASO C: Texto, Fecha, Listas -> CON comillas (ej: "id": "A1")
                else:
                    part = f'"{v.name}": "{{{v.name}}}"'
                
                json_parts.append(part)

            template = "{" + ", ".join(json_parts) + "}"
            
            # --- CONECTOR ---
            connector = self._create_connector(config, template, evt.name)
            
            for v in evt.variables:
                connector.add_variable(v)
            
            grp = Group(evt.name)
            grp.add_connector(connector)
            self.engine.add_event_group(evt, grp)
        
        self.engine_thread = threading.Thread(target=self.engine.start)
        self.engine_thread.daemon = True
        self.engine_thread.start()
        
        self.control.btn_start.config(state="disabled")
        self.control.btn_stop.config(state="normal")
    
    def _create_connector(self, config, template, event_name):
        conn_type = config["type"]
        options = config["options"]
        
        if conn_type == "MQTT":
            host = options["host"]
            topic = options["topic"]
            return MqttConnector(event_name, template, host=host, topic=topic, on_message_callback=self.control.log)
        
        elif conn_type == "RabbitMQ":
            host = options["host"]
            port = options["port"]
            user = options["user"]
            password = options["password"]
            queue = options["queue"]
            return AmqpConnector(event_name, template, host=host, port=port, user=user, password=password, queue=queue, on_message_callback=self.control.log)
        
        else:
            path = options["filepath"]
            return FileConnector(event_name, template, filepath=path, on_message_callback=self.control.log)
    
    def stop_simulation(self):
        if self.engine:
            self.engine.stop()
            self.control.btn_start.config(state="normal")
            self.control.btn_stop.config(state="disabled")