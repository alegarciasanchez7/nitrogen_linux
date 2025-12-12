"""
Implementación de 3.4.4 Tipo Fecha (Con soporte para Anomalías)
"""
import random
from datetime import datetime, timedelta
from .variable import Variable

class DateVariable(Variable):
    # AHORA ACEPTAMOS anomaly_prob y anomaly_value
    def __init__(self, name, strategy="now", base_date=None, end_date=None, 
                 increment_seconds=1, date_format="%Y-%m-%d %H:%M:%S",
                 anomaly_prob=0.0, anomaly_value="1970-01-01"):
        
        # Pasamos los datos de anomalía al padre
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.strategy = strategy 
        self.date_format = date_format
        self.base_date = base_date if base_date else datetime.now()
        self.end_date = end_date if end_date else datetime.now()
        self.increment_seconds = increment_seconds
        self.current_date_obj = self.base_date

    def generate(self):
        # 1. Comprobamos si toca fallar
        if self.check_anomaly():
            return self.current_value

        # 2. Generación normal
        val_date = None

        if self.strategy == "now":
            val_date = datetime.now()

        elif self.strategy == "fixed":
            val_date = self.base_date

        elif self.strategy == "increment":
            self.current_date_obj += timedelta(seconds=self.increment_seconds)
            val_date = self.current_date_obj

        elif self.strategy == "between":
            delta = self.end_date - self.base_date
            total_seconds = int(delta.total_seconds())
            if total_seconds > 0:
                random_seconds = random.randint(0, total_seconds)
                val_date = self.base_date + timedelta(seconds=random_seconds)
            else:
                val_date = self.base_date

        if val_date:
            self.current_value = val_date.strftime(self.date_format)
        
        return self.current_value