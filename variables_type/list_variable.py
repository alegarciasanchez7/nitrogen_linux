"""
Implementación de 3.4.3 Tipo Lista (Con Anomalías)
"""
import random
from .variable import Variable

class ListVariable(Variable):
    # AÑADIMOS anomaly_prob y anomaly_value al __init__
    def __init__(self, name, values, strategy="random", step=1, 
                 anomaly_prob=0.0, anomaly_value="ERROR"):
        
        # Pasamos los datos de anomalía a la clase padre (Variable)
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.values = values 
        self.strategy = strategy 
        self.step = step
        self.current_index = -step 

    def generate(self):
        # 1. Comprobamos si toca fallar (Anomalía)
        if self.check_anomaly():
            return self.current_value

        # 2. Generación normal
        if not self.values:
            return None

        if self.strategy == "random":
            self.current_value = random.choice(self.values)
        
        elif self.strategy == "serial":
            self.current_index += int(self.step) # Aseguramos que sea entero
            real_index = self.current_index % len(self.values)
            self.current_value = self.values[real_index]
            
        return self.current_value