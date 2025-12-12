import tkinter as tk
from tkinter import ttk

# Importar componentes GUI
from gui_components.components import ConnectionConfigPanel, VariableDesignerPanel, ControlPanel
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
        """Inicializa la interfaz de usuario"""
        # 1. Panel de configuración de conexión
        self.conn_config = ConnectionConfigPanel(self.root)
        self.conn_config.pack(fill="x", padx=10, pady=5)
        
        # 2. Panel de diseño de variables
        self.var_designer = VariableDesignerPanel(self.root, self.root)
        self.var_designer.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3. Panel de control
        self.control_panel = ControlPanel(self.root)
        self.control_panel.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 4. Inicializar handlers
        self.var_handlers = VariableHandlers(self.var_designer)
        
        # 5. Inicializar gestor de simulación
        self.sim_manager = SimulationManager(
            self.conn_config,
            self.var_handlers,
            self.control_panel
        )


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NitrogenGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error Tkinter: {e}")
