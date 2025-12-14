"""
Estructura de datos para un evento de simulación
"""
class EventConfig:
    def __init__(self, name="Nuevo Evento", frequency=1000):
        self.name = name
        self.frequency = frequency
        self.variables = [] # Lista de objetos Variable
        self.enabled = True

    def __str__(self):
        return f"{self.name} ({self.frequency}ms)"