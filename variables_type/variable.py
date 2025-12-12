"""
Clase base Variable - Representa la estructura padre para todos los tipos de datos
"""

class Variable:
    """Clase padre para todos los tipos de datos (Num, Str, Date, etc.)"""
    def __init__(self, name):
        self.name = name
        self.current_value = None

    def generate(self):
        """Método que debe ser sobrescrito por cada tipo de variable"""
        pass

    def get_value(self):
        return self.current_value
