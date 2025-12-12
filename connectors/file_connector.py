"""
Implementación de conector a Fichero (Log local)
"""
from .connector import Connector

class FileConnector(Connector):
    def __init__(self, name, template, filepath="datos_simulacion.txt", on_message_callback=None):
        super().__init__(name, template, on_message_callback)
        self.filepath = filepath
        
        # Opcional: Limpiar el fichero al iniciar
        with open(self.filepath, "w") as f:
            f.write("--- INICIO SIMULACION ---\n")

    def send(self):
        message = self._process_template()
        
        try:
            # Abrimos en modo 'a' (append) para añadir al final
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(message + "\n")
            
            # Feedback visual
            self.log(f"[{self.name}] FICHERO -> {self.filepath}: {message}")
            
        except Exception as e:
            self.log(f"[{self.name}] ERROR escribiendo fichero: {e}")