import time
from datetime import datetime
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable

# --- CLASE CONECTOR (Simulando Sección 3.3) ---

class Connector:
    """Representa un flujo de envío de datos [cite: 59]"""
    def __init__(self, name, template, output_type="console"):
        self.name = name
        self.template = template  # El formato del texto a enviar 
        self.output_type = output_type
        self.variables = {} # Diccionario de variables locales

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def _process_template(self):
        """Sustituye las variables en el texto.
        nITROGEN usa $#Rd.LO.Num#$, nosotros usaremos {NombreVariable} para simplificar.
        """
        output = self.template
        for var_name, var_obj in self.variables.items():
            # 1. Generar nuevo dato
            var_obj.generate()
            # 2. Sustituir en el texto
            # Usamos un reemplazo simple de string para simular la construcción del mensaje
            output = output.replace(f"{{{var_name}}}", str(var_obj.get_value()))
        return output

    def send(self):
        message = self._process_template()
        
        # Aquí implementaremos MQTT, TCP, Fichero más adelante 
        if self.output_type == "console":
            print(f"[{self.name}] Enviando: {message}")
        elif self.output_type == "file":
            with open(f"{self.name}.txt", "a") as f:
                f.write(message + "\n")

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

# --- EJEMPLO DE USO (Simulación de lo que harías en la GUI) ---

if __name__ == "__main__":
    # 1. Crear el motor
    engine = NitrogenEngine(frequency_ms=2000) # 2 segundos por tick para leerlo bien

    # --- VARIABLES ---
    
    # Numérica: Temperatura (20-30°C)
    temp_var = NumericVariable("Temperatura", 20, 30, strategy="random")
    
    # String: Número de Serie del dispositivo (Longitud fija 10, Mayúsculas y Números)
    # Mapeo manual: Fixed Size=10, UpperCase=Yes, Numbers=Yes, Lower=No, Sym=No
    serial_var = StringVariable("SerialNum", min_len=10, max_len=10, 
                                use_upper=True, use_lower=False, 
                                use_nums=True, use_sym=False)

    # String: Token de sesión (Longitud variable 15-20, Todo incluido)
    token_var = StringVariable("SessionToken", min_len=15, max_len=20, 
                               use_upper=True, use_lower=True, 
                               use_nums=True, use_sym=True)
    
    # TIPO LISTA: Días de la semana secuenciales [cite: 407]
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    dia_var = ListVariable("DiaSemana", dias, strategy="serial", step=1)

    # TIPO LISTA: Estado del sistema (Aleatorio con pesos simulados por repetición)
    estados = ["OK", "OK", "OK", "WARNING", "ERROR"] 
    estado_var = ListVariable("Status", estados, strategy="random")

    # TIPO FECHA: Timestamp incremental (simulando datos históricos)
    # Empieza el 1 de Enero de 2024 y avanza 1 hora por cada tick
    inicio = datetime(2024, 1, 1, 8, 0, 0)
    fecha_var = DateVariable("Timestamp", strategy="increment", 
                             base_date=inicio, increment_seconds=3600)

    # --- CONECTOR ---

    plantilla = (
        'DATA | {Timestamp} | Dia: {DiaSemana} | Temp: {Temperatura} C | Estado: {Status}'
    )
    
    connector_log = Connector("Log_Diario", plantilla)
    
    # Registramos las variables en el conector
    connector_log.add_variable(temp_var)
    connector_log.add_variable(dia_var)
    connector_log.add_variable(estado_var)
    connector_log.add_variable(fecha_var)

    # --- GRUPO Y ARRANQUE ---
    grupo_sensores = Group("Sensores_Planta_1")
    grupo_sensores.add_connector(connector_log)

    engine.add_group(grupo_sensores)
    engine.start()