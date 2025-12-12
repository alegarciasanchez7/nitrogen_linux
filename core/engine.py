"""
Motor principal de nITROGEN
"""
import time


class NitrogenEngine:
    """Motor principal de simulación (Configuración Global)"""
    def __init__(self, frequency_ms=1000):
        self.frequency_ms = frequency_ms
        self.groups = []
        self.running = False

    def add_group(self, group):
        self.groups.append(group)

    def start(self):
        self.running = True
        print(f"--- Iniciando nITROGEN (Linux) - Freq: {self.frequency_ms}ms ---")
        try:
            while self.running:
                for group in self.groups:
                    group.run_cycle()
                
                # Control de frecuencia
                time.sleep(self.frequency_ms / 1000.0)
        except KeyboardInterrupt:
            print("\nDeteniendo simulación...")
