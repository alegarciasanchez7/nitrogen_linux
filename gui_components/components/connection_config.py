"""
Panel de configuración de conexión (MQTT, RabbitMQ, Fichero)
"""
import tkinter as tk
from tkinter import ttk, filedialog


class ConnectionConfigPanel:
    def __init__(self, parent):
        self.parent = parent
        self.widgets_conn = {}
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="1. Configuración de Salida", padding=10)
        
        # Selector de Tipo de Conector
        ttk.Label(self.frame, text="Tipo Conector:").grid(row=0, column=0, padx=5)
        self.combo_conn_type = ttk.Combobox(
            self.frame, 
            values=["RabbitMQ", "MQTT", "Fichero"], 
            state="readonly", 
            width=10
        )
        self.combo_conn_type.current(0)
        self.combo_conn_type.grid(row=0, column=1, padx=5)
        self.combo_conn_type.bind("<<ComboboxSelected>>", self._toggle_conn_options)
        
        # Frame dinámico para opciones de conexión
        self.conn_options_frame = ttk.Frame(self.frame)
        self.conn_options_frame.grid(row=0, column=2, columnspan=4, sticky="w")
        
        self._toggle_conn_options()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def _toggle_conn_options(self, event=None):
        for w in self.conn_options_frame.winfo_children():
            w.destroy()
        self.widgets_conn = {}
        
        selection = self.combo_conn_type.get()
        if selection == "MQTT":
            self._show_mqtt_options()
        elif selection == "RabbitMQ":
            self._show_amqp_options()
        else:
            self._show_file_options()
    
    def _show_amqp_options(self):
        
        # 1. Host
        ttk.Label(self.conn_options_frame, text="Host:").pack(side="left", padx=(0, 2))
        e_h = ttk.Entry(self.conn_options_frame, width=12)
        e_h.insert(0, "localhost")
        e_h.pack(side="left", padx=2)
        self.widgets_conn["host"] = e_h
        
        # 2. Port
        ttk.Label(self.conn_options_frame, text="Port:").pack(side="left", padx=(5, 2))
        e_p = ttk.Entry(self.conn_options_frame, width=5)
        e_p.insert(0, "5672")
        e_p.pack(side="left", padx=2)
        self.widgets_conn["port"] = e_p
        
        # 3. User
        ttk.Label(self.conn_options_frame, text="User:").pack(side="left", padx=(5, 2))
        e_u = ttk.Entry(self.conn_options_frame, width=8)
        e_u.insert(0, "guest")
        e_u.pack(side="left", padx=2)
        self.widgets_conn["user"] = e_u

        # 4. Pass
        ttk.Label(self.conn_options_frame, text="Pass:").pack(side="left", padx=(5, 2))
        e_pw = ttk.Entry(self.conn_options_frame, width=8, show="*")
        e_pw.insert(0, "guest")
        e_pw.pack(side="left", padx=2)
        self.widgets_conn["password"] = e_pw
        
        # 5. Queue
        ttk.Label(self.conn_options_frame, text="Cola:").pack(side="left", padx=(5, 2))
        e_q = ttk.Entry(self.conn_options_frame, width=12)
        e_q.insert(0, "sensores_iot")
        e_q.pack(side="left", padx=2)
        self.widgets_conn["queue"] = e_q
    
    def _show_mqtt_options(self):
        ttk.Label(self.conn_options_frame, text="Broker:").pack(side="left")
        e_h = ttk.Entry(self.conn_options_frame)
        e_h.insert(0, "test.mosquitto.org")
        e_h.pack(side="left", padx=2)
        self.widgets_conn["host"] = e_h
        
        ttk.Label(self.conn_options_frame, text="Topic:").pack(side="left")
        e_t = ttk.Entry(self.conn_options_frame)
        e_t.insert(0, "nitrogen/linux")
        e_t.pack(side="left", padx=2)
        self.widgets_conn["topic"] = e_t
    
    def _show_file_options(self):
        f_container = ttk.Frame(self.conn_options_frame)
        f_container.pack(side="left", fill="x", expand=True)
        
        ttk.Label(f_container, text="Ruta Archivo:").pack(side="left")
        
        e_f = ttk.Entry(f_container, width=30)
        e_f.insert(0, "log_datos.txt")
        e_f.pack(side="left", padx=5)
        self.widgets_conn["filepath"] = e_f
        
        btn_browse = ttk.Button(f_container, text="📂 Examinar", command=self._open_file_dialog)
        btn_browse.pack(side="left")
    
    def _open_file_dialog(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("CSV", "*.csv"), ("Todos", "*.*")],
            title="Guardar Log de Simulación"
        )
        
        if filepath:
            self.widgets_conn["filepath"].delete(0, tk.END)
            self.widgets_conn["filepath"].insert(0, filepath)
    
    def get_config(self):
        """Retorna la configuración actual"""
        return {
            "type": self.combo_conn_type.get(),
            "options": self.widgets_conn
        }

    def set_config(self, config_data):
        """Restaura la configuración visual desde un diccionario de datos"""
        # 1. Tipo de Conector
        conn_type = config_data.get("type", "RabbitMQ")
        self.combo_conn_type.set(conn_type)
        
        # 2. Forzar actualización de la vista (mostrar los campos correctos)
        self._toggle_conn_options()
        
        # 3. Rellenar Opciones Dinámicas (Host, Port, Topic, etc.)
        options = config_data.get("options", {})
        
        # self.widgets_conn contiene las referencias a los Entries actuales
        for key, value in options.items():
            if key in self.widgets_conn:
                entry_widget = self.widgets_conn[key]
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(value))