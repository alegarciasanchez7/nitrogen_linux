"""
Implementación de 3.4.2 Tipo Cadena (Con Anomalías)
"""
import random
import string
import rstr
from .variable import Variable

class StringVariable(Variable):
    def __init__(self, name, strategy="random", 
                 min_len=10, max_len=10, 
                 use_upper=True, use_lower=True, use_nums=True, use_sym=False,
                 pattern=r"[A-Z]{3}-\d{3}",
                 anomaly_prob=0.0, anomaly_value="ERROR"):
        
        # Pasamos anomalía al padre
        super().__init__(name, anomaly_prob, anomaly_value)
        
        self.strategy = strategy 
        self.pattern = pattern
        self.min_len = min_len
        self.max_len = max_len
        self.use_upper = use_upper
        self.use_lower = use_lower
        self.use_nums = use_nums
        self.use_sym = use_sym
        
        self.char_pool = ""
        if use_upper: self.char_pool += string.ascii_uppercase
        if use_lower: self.char_pool += string.ascii_lowercase
        if use_nums:  self.char_pool += string.digits
        if use_sym:   self.char_pool += string.punctuation
        if not self.char_pool: self.char_pool = string.ascii_letters

    def generate(self):
        # 1. Chequeo de Anomalía
        if self.check_anomaly():
            return self.current_value

        # 2. Generación Normal
        if self.strategy == "regex":
            self.current_value = rstr.xeger(self.pattern)
        else:
            length = random.randint(self.min_len, self.max_len)
            self.current_value = ''.join(random.choice(self.char_pool) for _ in range(length))
        
        return self.current_value