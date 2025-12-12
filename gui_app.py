import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

# Importamos tu lógica
from nitrogen_linux import NitrogenEngine, Group
from connectors import MqttConnector
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable

class NitrogenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("nITROGEN Linux Edition - Generador IoT")
        self.root.geometry("900x600")
        
        # Estilos para que se vea moderno en Fedora
        style = ttk.Style()
        style.theme_use('clam') 

        self.engine = None
        self.engine_thread = None
        self.added_variables = [] # Lista para guardar las variables creadas

        self._init_ui()

    def _init_ui(self):
        # --- PANEL SUPERIOR: CONFIGURACIÓN MQTT ---
        config_frame = ttk.LabelFrame(self.root, text="1. Configuración de Conexión (MQTT)", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(config_frame, text="Broker Host:").grid(row=0, column=0, padx=5)
        self.entry_host = ttk.Entry(config_frame)
        self.entry_host.insert(0, "test.mosquitto.org")
        self.entry_host.grid(row=0, column=1, padx=5)

        ttk.Label(config_frame, text="Topic:").grid(row=0, column=2, padx=5)
        self.entry_topic = ttk.Entry(config_frame)
        self.entry_topic.insert(0, "nitrogen/linux/gui")
        self.entry_topic.grid(row=0, column=3, padx=5)

        ttk.Label(config_frame, text="Freq (ms):").grid(row=0, column=4, padx=5)
        self.entry_freq = ttk.Entry(config_frame, width=8)
        self.entry_freq.insert(0, "1000")
        self.entry_freq.grid(row=0, column=5, padx=5)

        # --- PANEL CENTRAL: GESTIÓN DE VARIABLES ---
        vars_frame = ttk.LabelFrame(self.root, text="2. Definición de Datos", padding=10)
        vars_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Izquierda: Formulario para añadir
        form_frame = ttk.Frame(vars_frame)
        form_frame.pack(side="left", fill="y", padx=5)

        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame)
        self.entry_var_name.pack(fill="x", pady=2)

        ttk.Label(form_frame, text="Tipo:").pack(anchor="w", pady=(10, 0))
        self.combo_type = ttk.Combobox(form_frame, values=["Numérico", "Texto", "Fecha", "Lista"])
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)

        # Botón Añadir
        ttk.Button(form_frame, text="Añadir Variable", command=self.add_variable).pack(pady=15, fill="x")

        # Derecha: Lista de variables añadidas
        list_frame = ttk.Frame(vars_frame)
        list_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.vars_listbox = tk.Listbox(list_frame)
        self.vars_listbox.pack(fill="both", expand=True)

        # --- PANEL INFERIOR: LOG Y CONTROL ---
        control_frame = ttk.LabelFrame(self.root, text="3. Control y Salida", padding=10)
        control_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x")

        self.btn_start = ttk.Button(btn_frame, text="▶ INICIAR SIMULACIÓN", command=self.start_simulation)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(btn_frame, text="⏹ DETENER", command=self.stop_simulation, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # Área de texto para logs (ScrolledText)
        self.log_area = tk.Text(control_frame, height=8, bg="#222", fg="#0f0")
        self.log_area.pack(fill="both", expand=True, pady=5)

    def log(self, message):
        """Escribe en la pantalla negra de abajo"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def add_variable(self):
        """Crea el objeto variable según lo seleccionado"""
        name = self.entry_var_name.get()
        v_type = self.combo_type.get()
        
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        var_obj = None
        desc = ""

        # Lógica simplificada de creación (valores por defecto para el examen)
        if v_type == "Numérico":
            var_obj = NumericVariable(name, 0, 100, strategy="random")
            desc = f"{name} (Num: 0-100)"
        elif v_type == "Texto":
            var_obj = StringVariable(name, min_len=5, max_len=8)
            desc = f"{name} (Txt: Aleatorio)"
        elif v_type == "Fecha":
            var_obj = DateVariable(name, strategy="now", date_format="%H:%M:%S")
            desc = f"{name} (Time: Actual)"
        elif v_type == "Lista":
            var_obj = ListVariable(name, ["Activo", "Inactivo", "Error"], strategy="random")
            desc = f"{name} (Lista: Estados)"

        if var_obj:
            self.added_variables.append(var_obj)
            self.vars_listbox.insert(tk.END, desc)
            self.entry_var_name.delete(0, tk.END)

    def start_simulation(self):
        if not self.added_variables:
            messagebox.showwarning("Aviso", "Añade al menos una variable primero.")
            return

        # 1. Configurar Motor
        freq = int(self.entry_freq.get())
        self.engine = NitrogenEngine(frequency_ms=freq)

        # 2. Construir Plantilla JSON Dinámica
        # Esto crea automáticamente un JSON: {"Var1": "{Var1}", "Var2": "{Var2}"}
        json_parts = []
        for v in self.added_variables:
            json_parts.append(f'"{v.name}": "{{{v.name}}}"') # Ojo al escape de llaves
        
        template_str = "{" + ", ".join(json_parts) + "}"
        self.log(f"Plantilla generada: {template_str}")

        # 3. Configurar Conector MQTT
        host = self.entry_host.get()
        topic = self.entry_topic.get()
        
        # Pasamos self.log como callback para ver los mensajes en la GUI
        connector = MqttConnector("GUI_Conn", template_str, host=host, topic=topic, on_message_callback=self.log)
        
        for v in self.added_variables:
            connector.add_variable(v)

        group = Group("GUI_Group")
        group.add_connector(connector)
        self.engine.add_group(group)

        # 4. Lanzar en un Hilo separado (IMPORTANTE para no congelar la ventana)
        self.engine_thread = threading.Thread(target=self.engine.start)
        self.engine_thread.daemon = True # Si cierras la ventana, muere el hilo
        self.engine_thread.start()

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

    def stop_simulation(self):
        if self.engine:
            self.engine.running = False
            self.log("--- Deteniendo simulación... ---")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")

if __name__ == "__main__":
    # Comprobar si tkinter está instalado (en Fedora a veces viene separado)
    try:
        root = tk.Tk()
        app = NitrogenGUI(root)
        root.mainloop()
    except ImportError:
        print("ERROR: Necesitas instalar tkinter. En Fedora: sudo dnf install python3-tkinter")