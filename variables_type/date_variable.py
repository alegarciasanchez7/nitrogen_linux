"""
Implementación de 3.4.4 Tipo Fecha
"""
import random
from datetime import datetime, timedelta
from .variable import Variable

class DateVariable(Variable):
    def __init__(self, name, strategy="now", base_date=None, end_date=None, 
                 increment_seconds=1, date_format="%Y-%m-%d %H:%M:%S"):
        super().__init__(name)
        self.strategy = strategy # "now", "fixed", "increment", "between"
        self.date_format = date_format
        
        # Configuración inicial
        # Si no se da fecha base, usamos la actual
        self.base_date = base_date if base_date else datetime.now()
        self.end_date = end_date if end_date else datetime.now()
        
        self.increment_seconds = increment_seconds
        
        # Estado interno para la estrategia 'increment'
        self.current_date_obj = self.base_date

    def generate(self):
        val_date = None

        if self.strategy == "now":
            # Fecha del sistema actual [cite: 498]
            val_date = datetime.now()

        elif self.strategy == "fixed":
            # Fecha fija constante [cite: 496]
            val_date = self.base_date

        elif self.strategy == "increment":
            # Inicio más incremento (Start plus Increment) [cite: 501]
            # Aumentamos el contador interno
            self.current_date_obj += timedelta(seconds=self.increment_seconds)
            val_date = self.current_date_obj

        elif self.strategy == "between":
            # Intervalo aleatorio (Between) [cite: 509]
            # Calculamos la diferencia total en segundos
            delta = self.end_date - self.base_date
            total_seconds = int(delta.total_seconds())
            # Elegimos un segundo aleatorio dentro del rango
            random_seconds = random.randint(0, total_seconds)
            val_date = self.base_date + timedelta(seconds=random_seconds)

        # Formatear la salida (Formats) [cite: 486]
        if val_date:
            self.current_value = val_date.strftime(self.date_format)
        
        return self.current_value