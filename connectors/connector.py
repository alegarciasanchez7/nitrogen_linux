"""
Clase Base Connector - Gestiona la plantilla y las variables
"""
class Connector:
    def __init__(self, name, template):
        self.name = name
        self.template = template
        self.variables = {} 

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def _process_template(self):
        """Sustituye variables en el texto {NombreVariable}"""
        output = self.template
        for var_name, var_obj in self.variables.items():
            # 1. Generar nuevo dato
            var_obj.generate()
            # 2. Sustituir en el texto
            output = output.replace(f"{{{var_name}}}", str(var_obj.get_value()))
        return output

    def send(self):
        """Método base: por defecto imprime en consola"""
        message = self._process_template()
        print(f"[{self.name}] CONSOLA: {message}")