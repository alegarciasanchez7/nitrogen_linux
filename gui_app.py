import tkinter as tk
from tkinter import ttk

# Importar componentes GUI
from gui_components.components import ConnectionConfigPanel, VariableDesignerPanel, ControlPanel, EventsListPanel
from gui_components.functions import VariableHandlers, SimulationManager
from gui_components.functions.config_manager import ConfigManager


class NitrogenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("nITROGEN Linux - Versión Final Examen")
        self.root.geometry("1100x800")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Inicializar UI
        self._init_ui()
        
        # --- Inicializar Gestor de Configuración ---
        # NOTA: Solo pasamos los paneles que tienen datos (Conexión y Lista de Eventos)
        self.config_manager = ConfigManager(
            self.conn_config, 
            self.events_panel
        )
        
        # --- Conectar los botones de Archivo ---
        # Lo hacemos aquí porque self.config_manager ya existe
        self.btn_load.config(command=self.config_manager.load_configuration)
        self.btn_save.config(command=self.config_manager.save_configuration)
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario con soporte multi-evento"""
        
        # --- 0. PANEL SUPERIOR (ARCHIVO) ---
        # Creamos la barra de botones arriba del todo
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill="x", padx=10, pady=(10, 5))
        
        # Botones (sin comando todavía)
        self.btn_load = ttk.Button(top_bar, text="Cargar Configuración")
        self.btn_load.pack(side="left", padx=(0, 5))
        
        self.btn_save = ttk.Button(top_bar, text="Guardar Configuración")
        self.btn_save.pack(side="left", padx=5)
        # -----------------------------------

        # 1. Panel de configuración de conexión (Arriba)
        self.conn_config = ConnectionConfigPanel(self.root)
        self.conn_config.pack(fill="x", padx=10, pady=5)

        # 2. Contenedor Central (Dividido: Lista Eventos | Diseñador)
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Panel Izquierdo: Lista de Eventos ---
        left_pane = ttk.Frame(middle_frame, width=280)
        left_pane.pack(side="left", fill="y", padx=(0, 5))
        left_pane.pack_propagate(False) # Forzar ancho fijo

        # --- Panel Derecho: Diseñador de Variables ---
        # Creamos primero el diseñador porque events_panel lo necesita para el callback
        self.var_designer = VariableDesignerPanel(
            middle_frame, 
            self.root,
            on_event_update_callback=self._on_event_update # Usamos un método wrapper
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
        self.var_handlers = VariableHandlers(self.var_designer)
        
        self.sim_manager = SimulationManager(
            self.conn_config,
            self.var_handlers,
            self.control_panel
        )
        self.sim_manager.events_source = self.events_panel

    def _on_event_update(self):
        """Wrapper para actualizar la visualización de la lista de eventos"""
        if hasattr(self, 'events_panel'):
            self.events_panel.update_current_event_display()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NitrogenGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error Tkinter: {e}")