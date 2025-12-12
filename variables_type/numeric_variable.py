"""
Implementación de 3.4.1 Tipo Numérico
"""
import random
from .variable import Variable


class NumericVariable(Variable):
    def __init__(self, name, min_val, max_val, strategy="random", step=1):
        super().__init__(name)
        self.min_val = min_val
        self.max_val = max_val
        self.strategy = strategy # random, sequential, constant [cite: 270]
        self.step = step
        self.current_value = min_val if strategy == "sequential" else 0

    def generate(self):
        if self.strategy == "random":
            # Genera aleatorio entre min y max [cite: 273]
            self.current_value = random.uniform(self.min_val, self.max_val)
            # Para simplificar, si el paso es 1, lo hacemos entero
            if self.step == 1:
                self.current_value = int(self.current_value)
        
        elif self.strategy == "sequential":
            # Secuencial simple [cite: 272]
            self.current_value += self.step
            if self.current_value > self.max_val:
                self.current_value = self.min_val
        
        elif self.strategy == "constant":
             # Constante [cite: 274]
            self.current_value = self.min_val
            
        return self.current_value
