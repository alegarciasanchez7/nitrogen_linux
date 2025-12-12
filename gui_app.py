import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Importamos tu lógica
from nitrogen_linux import NitrogenEngine, Group
from connectors import MqttConnector, FileConnector, AmqpConnector
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable

class NitrogenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("nITROGEN Linux - Versión Final Examen")
        self.root.geometry("1100x800")
        
        style = ttk.Style()
        style.theme_use('clam') 

        self.engine = None
        self.engine_thread = None
        self.added_variables = [] 
        self.dynamic_widgets = {}
        self.editing_index = None 

        self._init_ui()

    def _init_ui(self):
        # --- 1. CONFIGURACIÓN DE SALIDA (MQTT / FICHERO) ---
        config_frame = ttk.LabelFrame(self.root, text="1. Configuración de Salida", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)

        # Selector de Tipo de Conector
        ttk.Label(config_frame, text="Tipo Conector:").grid(row=0, column=0, padx=5)
        self.combo_conn_type = ttk.Combobox(config_frame, values=["RabbitMQ", "MQTT", "Fichero"], state="readonly", width=10)
        self.combo_conn_type.current(0) # RabbitMQ  por defecto
        self.combo_conn_type.grid(row=0, column=1, padx=5)
        self.combo_conn_type.bind("<<ComboboxSelected>>", self._toggle_conn_options)

        # Frame dinámico para opciones de conexión
        self.conn_options_frame = ttk.Frame(config_frame)
        self.conn_options_frame.grid(row=0, column=2, columnspan=4, sticky="w")
        
        self.widgets_conn = {} # Para guardar referencias a inputs de conexión
        self._show_mqtt_options() # Iniciar con opciones MQTT

        # Frecuencia (Común a todos)
        ttk.Label(config_frame, text="Freq (ms):").grid(row=0, column=6, padx=5)
        self.entry_freq = ttk.Entry(config_frame, width=8)
        self.entry_freq.insert(0, "1000")
        self.entry_freq.grid(row=0, column=7, padx=5)

        # --- 2. GESTIÓN DE VARIABLES ---
        vars_frame = ttk.LabelFrame(self.root, text="2. Diseñador de Variables", padding=10)
        vars_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Panel Izquierdo (Formulario)
        form_frame = ttk.Frame(vars_frame, width=400); form_frame.pack(side="left", fill="y", padx=5); form_frame.pack_propagate(False)

        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame); self.entry_var_name.pack(fill="x", pady=2)

        ttk.Label(form_frame, text="Tipo:").pack(anchor="w", pady=(5, 0))
        self.combo_type = ttk.Combobox(form_frame, state="readonly", values=["Numérico", "Texto", "Lista", "Fecha"])
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", self._update_dynamic_options)

        self.options_frame = ttk.LabelFrame(form_frame, text="Parámetros", padding=5)
        self.options_frame.pack(fill="x", pady=5)
        self._show_numeric_options() # Default

        # Panel Anomalía
        anomaly_frame = ttk.LabelFrame(form_frame, text="Anomalías (Fallos)", padding=5)
        anomaly_frame.pack(fill="x", pady=5)
        ttk.Label(anomaly_frame, text="Probabilidad (%):").grid(row=0,column=0); e=ttk.Entry(anomaly_frame, width=8); e.insert(0,"0"); e.grid(row=0,column=1)
        self.entry_anomaly_prob = e
        ttk.Label(anomaly_frame, text="Valor:").grid(row=0,column=2); e=ttk.Entry(anomaly_frame, width=10); e.insert(0,"ERR"); e.grid(row=0,column=3)
        self.entry_anomaly_val = e

        # Botones
        btn_box = ttk.Frame(form_frame); btn_box.pack(fill="x", pady=10)
        self.btn_add_update = ttk.Button(btn_box, text="⬇ Añadir Variable", command=self.add_or_update_variable); self.btn_add_update.pack(side="left", fill="x", expand=True)
        self.btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.cancel_edit, state="disabled"); self.btn_cancel.pack(side="right")

        # Panel Derecho (Lista)
        list_frame = ttk.Frame(vars_frame); list_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.vars_listbox = tk.Listbox(list_frame, bg="#f0f0f0"); self.vars_listbox.pack(fill="both", expand=True)
        self.vars_listbox.bind('<Double-Button-1>', lambda e: self.edit_selected_variable())
        
        l_btns = ttk.Frame(list_frame); l_btns.pack(fill="x", pady=5)
        ttk.Button(l_btns, text="Editar", command=self.edit_selected_variable).pack(side="left", fill="x", expand=True)
        ttk.Button(l_btns, text="Borrar", command=self.delete_variable).pack(side="left", fill="x", expand=True)

        # --- 3. CONTROL ---
        control_frame = ttk.LabelFrame(self.root, text="3. Control", padding=10)
        control_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.btn_start = ttk.Button(control_frame, text="▶ INICIAR SIMULACIÓN", command=self.start_simulation)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(control_frame, text="⏹ DETENER", command=self.stop_simulation, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.log_area = tk.Text(control_frame, height=8, bg="#222", fg="#0f0"); self.log_area.pack(fill="both", expand=True, pady=5)

    # --- GESTIÓN DINÁMICA CONEXIÓN ---
    def _toggle_conn_options(self, event=None):
        for w in self.conn_options_frame.winfo_children(): w.destroy()
        self.widgets_conn = {}
        
        selection = self.combo_conn_type.get()
        if selection == "MQTT":
            self._show_mqtt_options()
        elif selection == "RabbitMQ":
            self._show_amqp_options() # <--- NUEVA LLAMADA
        else:
            self._show_file_options()

    # --- NUEVO MÉTODO PARA MOSTRAR CAMPOS DE RABBITMQ ---
    def _show_amqp_options(self):
        ttk.Label(self.conn_options_frame, text="Host:").pack(side="left")
        e_h = ttk.Entry(self.conn_options_frame, width=15)
        e_h.insert(0, "localhost")
        e_h.pack(side="left", padx=2)
        self.widgets_conn["host"] = e_h
        
        ttk.Label(self.conn_options_frame, text="Cola (Queue):").pack(side="left")
        e_q = ttk.Entry(self.conn_options_frame, width=15)
        e_q.insert(0, "sensores_iot")
        e_q.pack(side="left", padx=2)
        self.widgets_conn["queue"] = e_q

    def _show_mqtt_options(self):
        ttk.Label(self.conn_options_frame, text="Broker:").pack(side="left")
        e_h = ttk.Entry(self.conn_options_frame); e_h.insert(0, "test.mosquitto.org"); e_h.pack(side="left", padx=2)
        self.widgets_conn["host"] = e_h
        
        ttk.Label(self.conn_options_frame, text="Topic:").pack(side="left")
        e_t = ttk.Entry(self.conn_options_frame); e_t.insert(0, "nitrogen/linux"); e_t.pack(side="left", padx=2)
        self.widgets_conn["topic"] = e_t

    def _show_file_options(self):
        # Frame contenedor para mantener el Entry y el Botón juntos
        f_container = ttk.Frame(self.conn_options_frame)
        f_container.pack(side="left", fill="x", expand=True)

        ttk.Label(f_container, text="Ruta Archivo:").pack(side="left")
        
        # Campo de texto (Entry)
        e_f = ttk.Entry(f_container, width=30)
        e_f.insert(0, "log_datos.txt") # Valor por defecto
        e_f.pack(side="left", padx=5)
        self.widgets_conn["filepath"] = e_f

        # Botón Examinar (NUEVO)
        btn_browse = ttk.Button(f_container, text="📂 Examinar", command=self._open_file_dialog)
        btn_browse.pack(side="left")

    def _open_file_dialog(self):
        # Abre el diálogo nativo de "Guardar como"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("CSV", "*.csv"), ("Todos", "*.*")],
            title="Guardar Log de Simulación"
        )
        
        # Si el usuario seleccionó algo (no dio a Cancelar)
        if filepath:
            self.widgets_conn["filepath"].delete(0, tk.END) # Borrar lo que había
            self.widgets_conn["filepath"].insert(0, filepath) # Poner la ruta nueva

    # --- GESTIÓN DINÁMICA VARIABLES ---
    def _update_dynamic_options(self, event=None):
        for w in self.options_frame.winfo_children(): w.destroy()
        self.dynamic_widgets = {}
        sel = self.combo_type.get()
        if sel == "Numérico": self._show_numeric_options()
        elif sel == "Texto": self._show_string_options()
        elif sel == "Lista": self._show_list_options()
        elif sel == "Fecha": self._show_date_options()

    def _show_numeric_options(self):
        # AÑADIDO: 'trend' a la lista de estrategias
        ttk.Label(self.options_frame, text="Rango (Min-Max):").pack()
        f = ttk.Frame(self.options_frame); f.pack()
        e1=ttk.Entry(f, width=8); e1.insert(0,"0"); e1.pack(side="left")
        ttk.Label(f, text="-").pack(side="left")
        e2=ttk.Entry(f, width=8); e2.insert(0,"100"); e2.pack(side="left")
        self.dynamic_widgets["min"]=e1; self.dynamic_widgets["max"]=e2
        
        ttk.Label(self.options_frame, text="Estrategia:").pack()
        c=ttk.Combobox(self.options_frame, values=["random","sequential","constant","trend"])
        c.current(0); c.pack()
        self.dynamic_widgets["strategy"]=c
        
        # AÑADIDO: Campo 'Step' vital para Secuencial y Tendencia
        ttk.Label(self.options_frame, text="Paso / Variación (Step):").pack()
        e_s=ttk.Entry(self.options_frame, width=8); e_s.insert(0,"1"); e_s.pack()
        self.dynamic_widgets["step"]=e_s

    def _show_string_options(self):
        # (Código simplificado de String, usa tu versión completa aquí si quieres)
        ttk.Label(self.options_frame, text="Longitud:").pack()
        e=ttk.Entry(self.options_frame); e.insert(0,"10"); e.pack(); self.dynamic_widgets["len"]=e

    def _show_list_options(self):
        ttk.Label(self.options_frame, text="Valores (CSV):").pack()
        t=tk.Text(self.options_frame, height=3, width=25); t.insert("1.0","ON,OFF"); t.pack(); self.dynamic_widgets["vals"]=t
        c=ttk.Combobox(self.options_frame, values=["random","serial"]); c.current(0); c.pack(); self.dynamic_widgets["strat"]=c

    def _show_date_options(self):
        ttk.Label(self.options_frame, text="Formato:").pack()
        e=ttk.Entry(self.options_frame); e.insert(0,"%H:%M:%S"); e.pack(); self.dynamic_widgets["fmt"]=e
        c=ttk.Combobox(self.options_frame, values=["now","increment"]); c.current(0); c.pack(); self.dynamic_widgets["strat"]=c

    # --- LÓGICA DE SIMULACIÓN ---
    def add_or_update_variable(self):
        name = self.entry_var_name.get()
        if not name: return
        try:
            v_type = self.combo_type.get()
            a_prob = float(self.entry_anomaly_prob.get())
            a_val = self.entry_anomaly_val.get()
            
            var = None
            desc = ""
            
            if v_type == "Numérico":
                mn = float(self.dynamic_widgets["min"].get())
                mx = float(self.dynamic_widgets["max"].get())
                strat = self.dynamic_widgets["strategy"].get()
                step = float(self.dynamic_widgets["step"].get()) # AÑADIDO
                
                # Intentar convertir anómalo a número si es posible
                try: val_anom = float(a_val)
                except: val_anom = a_val
                
                var = NumericVariable(name, mn, mx, strategy=strat, step=step, 
                                      anomaly_prob=a_prob, anomaly_value=val_anom)
                desc = f"{name} [Num: {strat} | Step {step}]"

            elif v_type == "Texto": # Simplificado
                l = int(self.dynamic_widgets["len"].get())
                var = StringVariable(name, min_len=l, max_len=l, anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [Txt]"
                
            elif v_type == "Lista":
                vals = self.dynamic_widgets["vals"].get("1.0", tk.END).replace("\n","").split(",")
                st = self.dynamic_widgets["strat"].get()
                var = ListVariable(name, vals, strategy=st, anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [List]"
                
            elif v_type == "Fecha":
                fmt = self.dynamic_widgets["fmt"].get()
                st = self.dynamic_widgets["strat"].get()
                var = DateVariable(name, strategy=st, date_format=fmt, anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [Date]"

            if self.editing_index is None:
                self.added_variables.append(var)
                self.vars_listbox.insert(tk.END, desc)
                self.entry_var_name.delete(0, tk.END)
            else:
                self.added_variables[self.editing_index] = var
                self.vars_listbox.config(state="normal")
                self.vars_listbox.delete(self.editing_index)
                self.vars_listbox.insert(self.editing_index, desc)
                self.cancel_edit()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_selected_variable(self):
        sel = self.vars_listbox.curselection()
        if not sel: return
        self.editing_index = sel[0]
        var = self.added_variables[self.editing_index]
        self.entry_var_name.delete(0, tk.END); self.entry_var_name.insert(0, var.name)
        self.btn_cancel.config(state="normal")
        # (Aquí deberías implementar la carga completa de valores al form, simplificado por espacio)

    def cancel_edit(self):
        self.editing_index = None
        self.btn_cancel.config(state="disabled")
        self.entry_var_name.delete(0, tk.END)

    def delete_variable(self):
        sel = self.vars_listbox.curselection()
        if sel:
            self.vars_listbox.delete(sel[0])
            del self.added_variables[sel[0]]

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n"); self.log_area.see(tk.END)

    def start_simulation(self):
        if not self.added_variables: return
        self.engine = NitrogenEngine(frequency_ms=int(self.entry_freq.get()))
        
        # Crear Plantilla JSON
        json_parts = [f'"{v.name}": "{{{v.name}}}"' for v in self.added_variables]
        template = "{" + ", ".join(json_parts) + "}"
        
        # SELECCIÓN DE CONECTOR
        conn_type = self.combo_conn_type.get()
        connector = None
        
        if conn_type == "MQTT":
            host = self.widgets_conn["host"].get()
            topic = self.widgets_conn["topic"].get()
            connector = MqttConnector("MQTT_Client", template, host=host, topic=topic, on_message_callback=self.log)
        
        elif conn_type == "RabbitMQ":  # <--- NUEVO BLOQUE
            host = self.widgets_conn["host"].get()
            queue = self.widgets_conn["queue"].get()
            connector = AmqpConnector("RabbitMQ", template, host=host, queue=queue, on_message_callback=self.log)

        else:
            path = self.widgets_conn["filepath"].get()
            connector = FileConnector("File_Logger", template, filepath=path, on_message_callback=self.log)
            
        for v in self.added_variables: connector.add_variable(v)
        
        grp = Group("Main"); grp.add_connector(connector); self.engine.add_group(grp)
        
        self.engine_thread = threading.Thread(target=self.engine.start); self.engine_thread.daemon=True; self.engine_thread.start()
        self.btn_start.config(state="disabled"); self.btn_stop.config(state="normal")

    def stop_simulation(self):
        if self.engine: self.engine.running=False; self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled")

if __name__ == "__main__":
    try: root = tk.Tk(); app = NitrogenGUI(root); root.mainloop()
    except: print("Error Tkinter")