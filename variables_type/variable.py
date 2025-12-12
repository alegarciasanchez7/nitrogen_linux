"""
Clase base Variable - Representa la estructura padre para todos los tipos de datos
"""
import random

class Variable:
    """Clase padre para todos los tipos de datos. Incluye soporte para Anomalías."""
    
    def __init__(self, name, anomaly_prob=0.0, anomaly_value=None):
        self.name = name
        self.current_value = None
        
        # Configuración de Anomalía (Manual Sección 3.4.1 "Allow Anomaly")
        self.anomaly_prob = anomaly_prob    # Probabilidad 0-100%
        self.anomaly_value = anomaly_value  # Valor a enviar si falla (ej: -999, "ERROR")

    def check_anomaly(self):
        """
        Determina si en este ciclo toca simular un fallo.
        Devuelve True si ocurre la anomalía.
        """
        if self.anomaly_prob > 0:
            # Generamos un número entre 0 y 100
            if random.uniform(0, 100) < self.anomaly_prob:
                self.current_value = self.anomaly_value
                return True
        return False

    def generate(self):
        """Método que debe ser sobrescrito por cada tipo de variable"""
        pass

    def get_value(self):
        return self.current_value