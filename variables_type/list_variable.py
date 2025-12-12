"""
Implementación de 3.4.3 Tipo Lista
"""
import random
from .variable import Variable

class ListVariable(Variable):
    def __init__(self, name, values, strategy="random", step=1):
        super().__init__(name)
        self.values = values # La lista de valores (ej: ["Lunes", "Martes"...])
        self.strategy = strategy # "random", "serial"
        self.step = step
        
        # Para estrategia secuencial, necesitamos recordar el índice actual
        # Iniciamos en -step para que la primera llamada (step) nos deje en 0
        self.current_index = -step 

    def generate(self):
        if not self.values:
            return None

        if self.strategy == "random":
            # Selección aleatoria simple 
            self.current_value = random.choice(self.values)
        
        elif self.strategy == "serial":
            # Avance secuencial [cite: 466]
            self.current_index += self.step
            
            # Comportamiento circular (Ignore rest/Loop) [cite: 474]
            # Si nos pasamos del tamaño, usamos el operador módulo
            real_index = self.current_index % len(self.values)
            self.current_value = self.values[real_index]
            
        return self.current_value