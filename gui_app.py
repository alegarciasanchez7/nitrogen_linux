import tkinter as tk
from tkinter import ttk

# Importar componentes GUI
from gui_components.components import ConnectionConfigPanel, VariableDesignerPanel, ControlPanel, EventsListPanel
from gui_components.functions import VariableHandlers, SimulationManager


class NitrogenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("nITROGEN Linux - Versión Final Examen")
        self.root.geometry("1100x800")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario con soporte multi-evento"""
        # 1. Panel de configuración de conexión (Arriba)
        self.conn_config = ConnectionConfigPanel(self.root)
        self.conn_config.pack(fill="x", padx=10, pady=5)

        # 2. Contenedor Central (Dividido: Lista Eventos | Diseñador)
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Panel Izquierdo: Lista de Eventos ---
        left_pane = ttk.Frame(middle_frame, width=280)
        left_pane.pack(side="left", fill="y", padx=(0, 5))
        # Forzamos que mantenga su ancho fijo para que no se colapse
        left_pane.pack_propagate(False)

        # --- Panel Derecho: Diseñador de Variables ---
        self.var_designer = VariableDesignerPanel(
            middle_frame, 
            self.root,
            on_event_update_callback=lambda: self.events_panel.update_current_event_display()
        )
        self.var_designer.pack(side="right", fill="both", expand=True)

        # --- Inicializar Lista de Eventos ---
        self.events_panel = EventsListPanel(
            left_pane, 
            on_event_selected_callback=self.var_designer.load_event
        )
        self.events_panel.pack(fill="both", expand=True)

        # 3. Panel de Control (Abajo)
        self.control_panel = ControlPanel(self.root)
        self.control_panel.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 4. Inicializar Lógica
        # Handlers para los botones del diseñador de variables
        self.var_handlers = VariableHandlers(self.var_designer)
        
        # Gestor de Simulación
        self.sim_manager = SimulationManager(
            self.conn_config,
            self.var_handlers,
            self.control_panel
        )
        # Inyectamos la fuente de eventos en el gestor para que sepa qué ejecutar
        self.sim_manager.events_source = self.events_panel


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NitrogenGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error Tkinter: {e}")
