"""
Implementación de 3.4.5 Tipo Punto (2D y 3D)
"""
import random
from .variable import Variable

class PointVariable(Variable):
    def __init__(self, name, dimension=3, 
                 x_range=(0, 100), y_range=(0, 100), z_range=(0, 100),
                 strategy="random", step=1.0,
                 anomaly_prob=0.0, anomaly_value="ERR_POINT"):
        
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.dimension = dimension # 2 o 3
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        self.strategy = strategy
        self.step = step
        
        # Estado actual (iniciamos en el centro de los rangos)
        self.curr_x = (x_range[0] + x_range[1]) / 2
        self.curr_y = (y_range[0] + y_range[1]) / 2
        self.curr_z = (z_range[0] + z_range[1]) / 2

    def _next_val(self, current, v_range):
        """Calcula el siguiente valor según la estrategia"""
        if self.strategy == "random":
            return random.uniform(v_range[0], v_range[1])
        
        elif self.strategy == "trend":
            # Movimiento aleatorio suave (Caminata)
            delta = random.uniform(-self.step, self.step)
            new_val = current + delta
            # Rebote si sale de los límites
            if new_val < v_range[0]: new_val = v_range[0]
            if new_val > v_range[1]: new_val = v_range[1]
            return new_val
        
        return current

    def generate(self):
        if self.check_anomaly():
            return self.current_value

        self.curr_x = self._next_val(self.curr_x, self.x_range)
        self.curr_y = self._next_val(self.curr_y, self.y_range)
        
        x_str = f"{self.curr_x:.2f}"
        y_str = f"{self.curr_y:.2f}"

        if self.dimension == 3:
            self.curr_z = self._next_val(self.curr_z, self.z_range)
            z_str = f"{self.curr_z:.2f}"
            self.current_value = f"({x_str}, {y_str}, {z_str})"
        else:
            self.current_value = f"({x_str}, {y_str})"
            
        return self.current_value