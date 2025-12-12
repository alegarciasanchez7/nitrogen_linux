"""
Implementación de 3.4.1 Tipo Numérico (Con Anomalías y Tendencias)
"""
import random
from .variable import Variable

class NumericVariable(Variable):
    def __init__(self, name, min_val, max_val, strategy="random", step=1, 
                 anomaly_prob=0.0, anomaly_value=-999):
        
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.min_val = min_val
        self.max_val = max_val
        self.strategy = strategy 
        self.step = step
        
        # Inicialización del valor
        if strategy == "sequential" or strategy == "trend":
            self.current_value = min_val
        else:
            self.current_value = 0

    def generate(self):
        # 1. Chequeo de Anomalía
        if self.check_anomaly():
            return self.current_value

        # 2. Estrategias
        if self.strategy == "random":
            self.current_value = random.uniform(self.min_val, self.max_val)
            if self.step == 1: self.current_value = int(self.current_value)
        
        elif self.strategy == "sequential":
            self.current_value += self.step
            if self.current_value > self.max_val:
                self.current_value = self.min_val
        
        elif self.strategy == "constant":
            self.current_value = self.min_val

        elif self.strategy == "trend":
            # TENDENCIA: Caminata aleatoria (Random Walk)
            # El nuevo valor es el anterior +/- un paso aleatorio
            delta = random.uniform(-self.step, self.step)
            self.current_value += delta
            
            # Control de rebote (si se sale de los límites, rebota hacia dentro)
            if self.current_value > self.max_val:
                self.current_value = self.max_val
            elif self.current_value < self.min_val:
                self.current_value = self.min_val

        # Redondeo para que sea legible si no es entero puro
        if isinstance(self.current_value, float):
            self.current_value = round(self.current_value, 2)
            
        return self.current_value