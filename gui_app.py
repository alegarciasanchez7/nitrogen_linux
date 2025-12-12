import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Importamos tu lógica
from nitrogen_linux import NitrogenEngine, Group
from connectors import MqttConnector, FileConnector, AmqpConnector
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable, PointVariable, BooleanVariable

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
        
        self.widgets_conn = {} 
        self._toggle_conn_options() 

        # Frecuencia
        ttk.Label(config_frame, text="Freq (ms):").grid(row=0, column=6, padx=5)
        self.entry_freq = ttk.Entry(config_frame, width=8)
        self.entry_freq.insert(0, "1000")
        self.entry_freq.grid(row=0, column=7, padx=5)

        # --- 2. GESTIÓN DE VARIABLES ---
        vars_frame = ttk.LabelFrame(self.root, text="2. Diseñador de Variables", padding=10)
        vars_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ===================================================================
        # ### INICIO CAMBIO SCROLL: Panel Izquierdo con Barra de Desplazamiento ###
        # ===================================================================
        
        # 1. Contenedor principal del panel izquierdo
        left_container = ttk.Frame(vars_frame, width=400)
        left_container.pack(side="left", fill="y", padx=5)
        
        # 2. Crear Canvas (zona dibujable) y Scrollbar
        canvas = tk.Canvas(left_container, width=370) # Un poco menos de 400 para dejar sitio al scroll
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        
        # 3. Frame interno que se moverá (aquí irán tus widgets)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Truco: Actualizar la región de scroll cuando el frame interno cambie de tamaño
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # 4. Meter el frame dentro del canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 5. Empaquetar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # IMPORTANTE: Asignamos 'form_frame' a nuestro nuevo frame desplazable
        # Así el resto de tu código (abajo) añade los botones en el sitio correcto sin cambios
        form_frame = self.scrollable_frame 
        
        # ===================================================================
        # ### FIN CAMBIO SCROLL ###
        # ===================================================================

        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame)
        self.entry_var_name.pack(fill="x", pady=2)

        ttk.Label(form_frame, text="Tipo:").pack(anchor="w", pady=(5, 0))
        # Asegúrate de tener todos los tipos aquí, incluido Punto y Booleano
        self.combo_type = ttk.Combobox(form_frame, state="readonly", values=["Numérico", "Texto", "Lista", "Fecha", "Punto", "Booleano"])
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", self._update_dynamic_options)

        self.options_frame = ttk.LabelFrame(form_frame, text="Parámetros", padding=5)
        self.options_frame.pack(fill="x", pady=5)
        self._show_numeric_options() 

        # Panel Anomalía
        anomaly_frame = ttk.LabelFrame(form_frame, text="Anomalías (Fallos)", padding=5)
        anomaly_frame.pack(fill="x", pady=5)
        ttk.Label(anomaly_frame, text="Probabilidad (%):").grid(row=0,column=0)
        self.entry_anomaly_prob = ttk.Entry(anomaly_frame, width=8)
        self.entry_anomaly_prob.insert(0,"0")
        self.entry_anomaly_prob.grid(row=0,column=1)
        
        ttk.Label(anomaly_frame, text="Valor:").grid(row=0,column=2)
        self.entry_anomaly_val = ttk.Entry(anomaly_frame, width=10)
        self.entry_anomaly_val.insert(0,"ERR")
        self.entry_anomaly_val.grid(row=0,column=3)

        # Botones
        btn_box = ttk.Frame(form_frame)
        btn_box.pack(fill="x", pady=10)
        self.btn_add_update = ttk.Button(btn_box, text="⬇ Añadir Variable", command=self.add_or_update_variable)
        self.btn_add_update.pack(side="left", fill="x", expand=True)
        self.btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.cancel_edit, state="disabled")
        self.btn_cancel.pack(side="right")

        # Panel Derecho (Lista)
        list_frame = ttk.Frame(vars_frame)
        list_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.vars_listbox = tk.Listbox(list_frame, bg="#f0f0f0")
        self.vars_listbox.pack(fill="both", expand=True)
        self.vars_listbox.bind('<Double-Button-1>', lambda e: self.edit_selected_variable())
        
        l_btns = ttk.Frame(list_frame)
        l_btns.pack(fill="x", pady=5)
        ttk.Button(l_btns, text="Editar", command=self.edit_selected_variable).pack(side="left", fill="x", expand=True)
        ttk.Button(l_btns, text="Borrar", command=self.delete_variable).pack(side="left", fill="x", expand=True)

        # --- 3. CONTROL ---
        control_frame = ttk.LabelFrame(self.root, text="3. Control", padding=10)
        control_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame para los botones (arriba)
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill="x", pady=(0, 5))
        
        self.btn_start = ttk.Button(buttons_frame, text="▶ INICIAR SIMULACIÓN", command=self.start_simulation)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(buttons_frame, text="⏹ DETENER", command=self.stop_simulation, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        # Consola de logs (abajo)
        self.log_area = tk.Text(control_frame, height=8, bg="#222", fg="#0f0")
        self.log_area.pack(fill="both", expand=True)

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
        elif sel == "Punto": self._show_point_options()
        elif sel == "Booleano": self._show_boolean_options()

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
        # Selector de Modo
        ttk.Label(self.options_frame, text="Modo:").pack(anchor="w")
        mode_combo = ttk.Combobox(self.options_frame, values=["Aleatorio", "Regex (Patrón)"], state="readonly")
        mode_combo.current(0)
        mode_combo.pack(fill="x", pady=2)
        self.dynamic_widgets["str_mode"] = mode_combo

        # Frame contenedor para los parámetros cambiantes
        param_container = ttk.Frame(self.options_frame)
        param_container.pack(fill="both", expand=True, pady=5)
        
        def toggle_params(event=None):
            # Limpiar opciones anteriores
            for widget in param_container.winfo_children():
                widget.destroy()
            
            mode = mode_combo.get()
            
            if mode == "Regex (Patrón)":
                ttk.Label(param_container, text="Expresión Regular:").pack(anchor="w")
                entry_regex = ttk.Entry(param_container)
                entry_regex.insert(0, r"[A-Z]{3}-\d{3}") 
                entry_regex.pack(fill="x")
                self.dynamic_widgets["regex_pattern"] = entry_regex
                
                # Ayuda visual
                ttk.Label(param_container, text=r"Ej: \d{4}[A-Z] (Matrícula)", font=("Arial", 8)).pack(anchor="w")
                
            else: # Modo Aleatorio
                f = ttk.Frame(param_container)
                f.pack(fill="x")
                ttk.Label(f, text="Min Len:").pack(side="left")
                min_l = ttk.Entry(f, width=5); min_l.insert(0, "5"); min_l.pack(side="left", padx=2)
                self.dynamic_widgets["min_len"] = min_l

                ttk.Label(f, text="Max Len:").pack(side="left")
                max_l = ttk.Entry(f, width=5); max_l.insert(0, "10"); max_l.pack(side="left", padx=2)
                self.dynamic_widgets["max_len"] = max_l

                # Checkboxes
                self.dynamic_widgets["upper"] = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_container, text="A-Z", variable=self.dynamic_widgets["upper"]).pack(anchor="w")
                self.dynamic_widgets["nums"] = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_container, text="0-9", variable=self.dynamic_widgets["nums"]).pack(anchor="w")
                self.dynamic_widgets["syms"] = tk.BooleanVar(value=False)
                ttk.Checkbutton(param_container, text="Simbolos", variable=self.dynamic_widgets["syms"]).pack(anchor="w")

        # Vincular el evento y ejecutarlo una vez al inicio
        mode_combo.bind("<<ComboboxSelected>>", toggle_params)
        toggle_params()
    
    def _show_list_options(self):
        ttk.Label(self.options_frame, text="Valores (CSV):").pack()
        t=tk.Text(self.options_frame, height=3, width=25); t.insert("1.0","ON,OFF"); t.pack(); self.dynamic_widgets["vals"]=t
        c=ttk.Combobox(self.options_frame, values=["random","serial"]); c.current(0); c.pack(); self.dynamic_widgets["strat"]=c

    def _show_date_options(self):
        ttk.Label(self.options_frame, text="Formato:").pack()
        e=ttk.Entry(self.options_frame); e.insert(0,"%H:%M:%S"); e.pack(); self.dynamic_widgets["fmt"]=e
        c=ttk.Combobox(self.options_frame, values=["now","increment"]); c.current(0); c.pack(); self.dynamic_widgets["strat"]=c

    def _show_point_options(self):
        # Selector Dimensiones
        ttk.Label(self.options_frame, text="Dimensión:").pack()
        c_dim = ttk.Combobox(self.options_frame, values=["2D", "3D"], state="readonly")
        c_dim.current(1) # 3D por defecto
        c_dim.pack()
        self.dynamic_widgets["dim"] = c_dim

        # Frame para rangos
        f_r = ttk.Frame(self.options_frame)
        f_r.pack(pady=5)

        # Rango X
        ttk.Label(f_r, text="X (Min-Max):").grid(row=0, column=0)
        ex1=ttk.Entry(f_r, width=5); ex1.insert(0,"0"); ex1.grid(row=0, column=1)
        ex2=ttk.Entry(f_r, width=5); ex2.insert(0,"100"); ex2.grid(row=0, column=2)
        self.dynamic_widgets["x_min"] = ex1; self.dynamic_widgets["x_max"] = ex2

        # Rango Y
        ttk.Label(f_r, text="Y (Min-Max):").grid(row=1, column=0)
        ey1=ttk.Entry(f_r, width=5); ey1.insert(0,"0"); ey1.grid(row=1, column=1)
        ey2=ttk.Entry(f_r, width=5); ey2.insert(0,"100"); ey2.grid(row=1, column=2)
        self.dynamic_widgets["y_min"] = ey1; self.dynamic_widgets["y_max"] = ey2

        # Rango Z (guardamos referencias a los widgets para poder ocultarlos/mostrarlos)
        z_label = ttk.Label(f_r, text="Z (Min-Max):")
        z_label.grid(row=2, column=0)
        ez1=ttk.Entry(f_r, width=5); ez1.insert(0,"0"); ez1.grid(row=2, column=1)
        ez2=ttk.Entry(f_r, width=5); ez2.insert(0,"100"); ez2.grid(row=2, column=2)
        self.dynamic_widgets["z_min"] = ez1
        self.dynamic_widgets["z_max"] = ez2
        self.dynamic_widgets["z_label"] = z_label

        # Función para mostrar/ocultar Z según dimensión
        def toggle_z_axis(event=None):
            dim = c_dim.get()
            if dim == "2D":
                # Ocultar widgets de Z
                z_label.grid_remove()
                ez1.grid_remove()
                ez2.grid_remove()
            else:
                # Mostrar widgets de Z
                z_label.grid()
                ez1.grid()
                ez2.grid()
        
        # Vincular evento y ejecutar al inicio
        c_dim.bind("<<ComboboxSelected>>", toggle_z_axis)
        toggle_z_axis()

        # Estrategia y Paso
        ttk.Label(self.options_frame, text="Estrategia:").pack()
        c_st = ttk.Combobox(self.options_frame, values=["random", "trend"])
        c_st.current(0); c_st.pack()
        self.dynamic_widgets["strat"] = c_st
        
        ttk.Label(self.options_frame, text="Paso (Speed):").pack()
        e_sp = ttk.Entry(self.options_frame, width=5); e_sp.insert(0, "1.0"); e_sp.pack()
        self.dynamic_widgets["step"] = e_sp

    def _show_boolean_options(self):
        ttk.Label(self.options_frame, text="Estrategia:").pack(anchor="w")
        c_strat = ttk.Combobox(self.options_frame, values=["random", "alternating", "constant"], state="readonly")
        c_strat.current(0)
        c_strat.pack(fill="x", pady=2)
        self.dynamic_widgets["strat"] = c_strat

        # Panel para opciones dinámicas según estrategia
        sub_frame = ttk.Frame(self.options_frame)
        sub_frame.pack(fill="x", pady=5)

        def update_sub_options(event=None):
            for w in sub_frame.winfo_children(): w.destroy()
            strat = c_strat.get()
            
            if strat == "random":
                ttk.Label(sub_frame, text="Probabilidad True (%):").pack(side="left")
                e_prob = ttk.Entry(sub_frame, width=5)
                e_prob.insert(0, "50")
                e_prob.pack(side="left", padx=5)
                self.dynamic_widgets["true_prob"] = e_prob
            else:
                # Para constant o alternating (valor inicial)
                lbl = "Valor Fijo:" if strat == "constant" else "Valor Inicial:"
                ttk.Label(sub_frame, text=lbl).pack(side="left")
                c_val = ttk.Combobox(sub_frame, values=["True", "False"], state="readonly", width=8)
                c_val.current(0)
                c_val.pack(side="left", padx=5)
                self.dynamic_widgets["init_val"] = c_val

        c_strat.bind("<<ComboboxSelected>>", update_sub_options)
        update_sub_options() # Ejecutar al inicio

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

            elif v_type == "Texto":
                mode = self.dynamic_widgets["str_mode"].get()
                
                # Intentar leer anomalía (si no es numérico, el valor anómalo se queda como texto)
                try: a_prob = float(self.entry_anomaly_prob.get())
                except: a_prob = 0.0
                a_val = self.entry_anomaly_val.get()

                if mode == "Regex (Patrón)":
                    pat = self.dynamic_widgets["regex_pattern"].get()
                    var = StringVariable(name, strategy="regex", pattern=pat, 
                                           anomaly_prob=a_prob, anomaly_value=a_val)
                    desc = f"{name} [Regex: {pat}]"
                else:
                    # Modo Aleatorio
                    mn = int(self.dynamic_widgets["min_len"].get())
                    mx = int(self.dynamic_widgets["max_len"].get())
                    up = self.dynamic_widgets["upper"].get()
                    nu = self.dynamic_widgets["nums"].get()
                    sy = self.dynamic_widgets["syms"].get()
                    
                    var = StringVariable(name, strategy="random", min_len=mn, max_len=mx, 
                                           use_upper=up, use_nums=nu, use_sym=sy,
                                           anomaly_prob=a_prob, anomaly_value=a_val)
                    desc = f"{name} [Txt: {mn}-{mx}]"
                
                # Añadir info de anomalía a la descripción si existe
                if a_prob > 0: desc += f" | ⚠ {a_prob}%"
                
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

            elif v_type == "Punto":
                dim_str = self.dynamic_widgets["dim"].get()
                dim = 2 if dim_str == "2D" else 3
                
                xr = (float(self.dynamic_widgets["x_min"].get()), float(self.dynamic_widgets["x_max"].get()))
                yr = (float(self.dynamic_widgets["y_min"].get()), float(self.dynamic_widgets["y_max"].get()))
                zr = (float(self.dynamic_widgets["z_min"].get()), float(self.dynamic_widgets["z_max"].get()))
                
                st = self.dynamic_widgets["strat"].get()
                step = float(self.dynamic_widgets["step"].get())
                
                var = PointVariable(name, dimension=dim, x_range=xr, y_range=yr, z_range=zr, 
                                    strategy=st, step=step, anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [Punto {dim}D]"
            
            elif v_type == "Booleano":
                strat = self.dynamic_widgets["strat"].get()
                prob = 50.0
                init_val = True
                
                if strat == "random":
                    prob = float(self.dynamic_widgets["true_prob"].get())
                else:
                    init_val = (self.dynamic_widgets["init_val"].get() == "True")
                
                var = BooleanVariable(name, strategy=strat, true_prob=prob, initial_value=init_val,
                                      anomaly_prob=a_prob, anomaly_value=a_val)
                
                if strat == "random":
                    desc = f"{name} [Bool: {prob}% True]"
                else:
                    desc = f"{name} [Bool: {strat}]"

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
        
        index = sel[0]
        var = self.added_variables[index]
        self.editing_index = index 
        
        # 1. Ajustar UI al modo edición
        self.btn_add_update.config(text="💾 Guardar Cambios")
        self.btn_cancel.config(state="normal")
        self.vars_listbox.config(state="disabled")

        # 2. Rellenar Datos Comunes (Nombre y Anomalías)
        self.entry_var_name.delete(0, tk.END)
        self.entry_var_name.insert(0, var.name)
        
        # Cargar datos de Anomalía (Importante: Manejar si es None)
        self.entry_anomaly_prob.delete(0, tk.END)
        self.entry_anomaly_prob.insert(0, str(var.anomaly_prob))
        
        self.entry_anomaly_val.delete(0, tk.END)
        self.entry_anomaly_val.insert(0, str(var.anomaly_value))
        
        # 3. Detectar Tipo y Rellenar campos específicos
        if isinstance(var, NumericVariable):
            self.combo_type.set("Numérico")
            self._update_dynamic_options() # Recarga el panel vacío
            
            # Rellenar campos numéricos
            self.dynamic_widgets["min"].delete(0, tk.END); self.dynamic_widgets["min"].insert(0, str(var.min_val))
            self.dynamic_widgets["max"].delete(0, tk.END); self.dynamic_widgets["max"].insert(0, str(var.max_val))
            self.dynamic_widgets["step"].delete(0, tk.END); self.dynamic_widgets["step"].insert(0, str(var.step))
            self.dynamic_widgets["strategy"].set(var.strategy)
            
        elif isinstance(var, StringVariable):
            self.combo_type.set("Texto")
            self._update_dynamic_options() # Carga el panel inicial de texto
            
            if var.strategy == "regex":
                # Si era Regex, cambiamos el combo y forzamos la actualización visual
                self.dynamic_widgets["str_mode"].set("Regex (Patrón)")
                self.dynamic_widgets["str_mode"].event_generate("<<ComboboxSelected>>")
                self.root.update_idletasks() # Truco para asegurar que los widgets existen antes de escribir
                
                self.dynamic_widgets["regex_pattern"].delete(0, tk.END)
                self.dynamic_widgets["regex_pattern"].insert(0, var.pattern)
            else:
                # Si era Aleatorio
                self.dynamic_widgets["str_mode"].set("Aleatorio")
                self.dynamic_widgets["str_mode"].event_generate("<<ComboboxSelected>>")
                self.root.update_idletasks()
                
                self.dynamic_widgets["min_len"].delete(0, tk.END); self.dynamic_widgets["min_len"].insert(0, str(var.min_len))
                self.dynamic_widgets["max_len"].delete(0, tk.END); self.dynamic_widgets["max_len"].insert(0, str(var.max_len))
                self.dynamic_widgets["upper"].set(var.use_upper)
                self.dynamic_widgets["nums"].set(var.use_nums)
                self.dynamic_widgets["syms"].set(var.use_sym)

        elif isinstance(var, ListVariable):
            self.combo_type.set("Lista")
            self._update_dynamic_options()
            
            # Convertir la lista de vuelta a texto CSV
            text_val = ", ".join(var.values)
            self.dynamic_widgets["vals"].delete("1.0", tk.END)
            self.dynamic_widgets["vals"].insert("1.0", text_val)
            self.dynamic_widgets["strat"].set(var.strategy)

        elif isinstance(var, DateVariable):
            self.combo_type.set("Fecha")
            self._update_dynamic_options()
            
            self.dynamic_widgets["fmt"].delete(0, tk.END)
            self.dynamic_widgets["fmt"].insert(0, var.date_format)
            self.dynamic_widgets["strat"].set(var.strategy)

        elif isinstance(var, PointVariable):
            self.combo_type.set("Punto")
            self._update_dynamic_options()
            
            # Cargar Dimensión
            dim_str = "3D" if var.dimension == 3 else "2D"
            self.dynamic_widgets["dim"].set(dim_str)
            
            # Forzar actualización visual 2D/3D 
            self.dynamic_widgets["dim"].event_generate("<<ComboboxSelected>>")
            self.root.update_idletasks()

            self.dynamic_widgets["strat"].set(var.strategy)
            self.dynamic_widgets["step"].delete(0, tk.END); self.dynamic_widgets["step"].insert(0, str(var.step))
            
            # Rangos
            self.dynamic_widgets["x_min"].delete(0, tk.END); self.dynamic_widgets["x_min"].insert(0, str(var.x_range[0]))
            self.dynamic_widgets["x_max"].delete(0, tk.END); self.dynamic_widgets["x_max"].insert(0, str(var.x_range[1]))
            
            self.dynamic_widgets["y_min"].delete(0, tk.END); self.dynamic_widgets["y_min"].insert(0, str(var.y_range[0]))
            self.dynamic_widgets["y_max"].delete(0, tk.END); self.dynamic_widgets["y_max"].insert(0, str(var.y_range[1]))
            
            self.dynamic_widgets["z_min"].delete(0, tk.END); self.dynamic_widgets["z_min"].insert(0, str(var.z_range[0]))
            self.dynamic_widgets["z_max"].delete(0, tk.END); self.dynamic_widgets["z_max"].insert(0, str(var.z_range[1]))

        elif isinstance(var, BooleanVariable):
            self.combo_type.set("Booleano")
            self._update_dynamic_options()
            
            self.dynamic_widgets["strat"].set(var.strategy)
            self.dynamic_widgets["strat"].event_generate("<<ComboboxSelected>>") # Forzar refresco visual
            self.root.update_idletasks()
            
            if var.strategy == "random":
                self.dynamic_widgets["true_prob"].delete(0, tk.END)
                self.dynamic_widgets["true_prob"].insert(0, str(var.true_prob))
            else:
                val_str = "True" if var.current_value else "False"
                # Pequeño truco para recuperar el valor inicial en alternating
                if var.strategy == "alternating": 
                     # Como alternating invierte, el valor "inicial" visual es el inverso del actual guardado
                     # o simplemente mostramos el estado actual como punto de partida
                     pass 
                self.dynamic_widgets["init_val"].set(val_str)

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
        json_parts = [f'"{v.name}": "{{{v.name}}}"' for v in self.added_variables if v is not None]
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