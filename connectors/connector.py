"""
Clase Base Connector - Gestiona la plantilla y las variables
"""
class Connector:
    # AÑADIDO: on_message_callback=None
    def __init__(self, name, template, on_message_callback=None):
        self.name = name
        self.template = template
        self.variables = {} 
        self.on_message_callback = on_message_callback # Guardamos la función

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def _process_template(self):
        """Sustituye variables en el texto {NombreVariable}"""
        output = self.template
        for var_name, var_obj in self.variables.items():
            var_obj.generate()
            output = output.replace(f"{{{var_name}}}", str(var_obj.get_value()))
        return output

    # NUEVO METODO: Gestiona si se imprime en consola o se manda a la GUI
    def log(self, message):
        if self.on_message_callback:
            self.on_message_callback(message)
        else:
            print(message)

    def send(self):
        """Método base: por defecto imprime en consola"""
        message = self._process_template()
        # CAMBIO: Usamos self.log en vez de print
        self.log(f"[{self.name}] CONSOLA: {message}")