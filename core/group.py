"""
Clase Group - Agrupa conectores
"""


class Group:
    """Agrupa conectores (Simulando Sección 3.1 - Panel Central)"""
    def __init__(self, name):
        self.name = name
        self.connectors = []

    def add_connector(self, connector):
        self.connectors.append(connector)

    def run_cycle(self):
        """Ejecuta un ciclo de envío para todos sus conectores"""
        for conn in self.connectors:
            conn.send()
