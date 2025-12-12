"""
Implementación de 3.4.2 Tipo Cadena
"""
import random
import string
from .variable import Variable


class StringVariable(Variable):
    def __init__(self, name, min_len=10, max_len=10, use_upper=True, use_lower=True, use_nums=True, use_sym=False):
        super().__init__(name)
        self.min_len = min_len
        self.max_len = max_len
        
        # Configuración de los conjuntos de caracteres (Fig. 8 del manual)
        self.char_pool = ""
        if use_upper:
            self.char_pool += string.ascii_uppercase # A-Z
        if use_lower:
            self.char_pool += string.ascii_lowercase # a-z
        if use_nums:
            self.char_pool += string.digits          # 0-9
        if use_sym:
            self.char_pool += string.punctuation     # !#$%&...

        # Validación para evitar errores si no se selecciona nada
        if not self.char_pool:
            self.char_pool = string.ascii_letters # Por defecto solo letras

    def generate(self):
        # 1. Determinar longitud para este ciclo (Fija o Variable)
        # Si min y max son iguales, es tamaño fijo [cite: 369]
        length = random.randint(self.min_len, self.max_len)
        
        # 2. Generar la cadena aleatoria seleccionando del "pool"
        # Esto simula las opciones de Upper, Lower, Numbers, Symbols
        self.current_value = ''.join(random.choice(self.char_pool) for _ in range(length))
        
        return self.current_value
