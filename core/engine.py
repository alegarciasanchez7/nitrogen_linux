"""
Motor principal de nITROGEN
"""
import threading
import time


class NitrogenEngine:
    """Motor principal de simulación"""
    def __init__(self):
        self.events = []
        self.running = False

    def add_event_group(self, event_config, group):
        self.events.append((event_config, group))

    def start(self):
        self.running = True
        print(f"--- Iniciando nITROGEN (Linux) ---")

        threads = []
        for evt_config, group in self.events:
            t = threading.Thread(target=self._run_event_loop, args=(evt_config, group))
            t.daemon = True
            t.start()
            threads.append(t)

        # Hilo principal espera o maneja parada global
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def _run_event_loop(self, evt_config, group):
        """Bucle específico para un evento"""
        print(f"-> Iniciando hilo para '{evt_config.name}' a {evt_config.frequency}ms")
        while self.running:
            group.run_cycle()
            time.sleep(evt_config.frequency / 1000.0)

    def stop(self):
        self.running = False
