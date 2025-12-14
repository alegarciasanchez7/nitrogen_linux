"""
Implementación de Tipo Booleano (Personalizado)
"""
import random
from .variable import Variable

class BooleanVariable(Variable):
    def __init__(self, name, strategy="random", true_prob=50.0, initial_value=True,
                 anomaly_prob=0.0, anomaly_value="ERROR"):
        
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.strategy = strategy # "random", "alternating", "constant"
        self.true_prob = true_prob # Probabilidad de True (0-100)
        self.initial_value = initial_value
        
        # Para strategy "constant" o inicio de "alternating"
        self.current_value = initial_value 
        
        # Para alternating, necesitamos saber el estado anterior
        if strategy == "alternating":
            self.current_value = not initial_value

    def generate(self):
        # 1. Chequeo de Anomalía
        if self.check_anomaly():
            return self.current_value

        # 2. Estrategias
        if self.strategy == "random":
            # Genera True si el número aleatorio (0-100) es menor que la probabilidad
            self.current_value = random.uniform(0, 100) < self.true_prob
            
        elif self.strategy == "alternating":
            # Invierte el valor actual
            self.current_value = not self.current_value
            
        elif self.strategy == "constant":
            # Mantiene el valor inicial
            pass
            
        return self.current_value