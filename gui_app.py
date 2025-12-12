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
        self.root.title("nITROGEN Linux Edition - Generador IoT Avanzado")
        self.root.geometry("1000x750") # Un poco más alto
        
        style = ttk.Style()
        style.theme_use('clam') 

        self.engine = None
        self.engine_thread = None
        self.added_variables = [] 
        self.dynamic_widgets = {}
        
        # Estado de edición
        self.editing_index = None # None significa modo "Crear nuevo"

        self._init_ui()

    def _init_ui(self):
        # --- 1. CONFIGURACIÓN MQTT ---
        config_frame = ttk.LabelFrame(self.root, text="1. Configuración MQTT", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(config_frame, text="Broker:").grid(row=0, column=0, padx=5)
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

        # --- 2. GESTIÓN DE VARIABLES ---
        vars_frame = ttk.LabelFrame(self.root, text="2. Diseñador de Variables", padding=10)
        vars_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # == COLUMNA IZQUIERDA: FORMULARIO ==
        form_frame = ttk.Frame(vars_frame, width=400)
        form_frame.pack(side="left", fill="y", padx=5)
        form_frame.pack_propagate(False)

        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame)
        self.entry_var_name.pack(fill="x", pady=2)

        ttk.Label(form_frame, text="Tipo de Dato:").pack(anchor="w", pady=(10, 0))
        self.combo_type = ttk.Combobox(form_frame, state="readonly", 
                                     values=["Numérico", "Texto", "Lista", "Fecha"])
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", self._update_dynamic_options)

        # Frame dinámico
        self.options_frame = ttk.LabelFrame(form_frame, text="Parámetros Específicos", padding=5)
        self.options_frame.pack(fill="x", pady=10)
        self._show_numeric_options() # Defecto

        # BOTONES DEL FORMULARIO
        btn_box = ttk.Frame(form_frame)
        btn_box.pack(fill="x", pady=10)
        
        self.btn_add_update = ttk.Button(btn_box, text="⬇ Añadir Variable", command=self.add_or_update_variable)
        self.btn_add_update.pack(side="left", fill="x", expand=True)
        
        self.btn_cancel = ttk.Button(btn_box, text="Cancelar", command=self.cancel_edit, state="disabled")
        self.btn_cancel.pack(side="right", padx=(5,0))

        # == COLUMNA DERECHA: LISTA ==
        list_frame = ttk.Frame(vars_frame)
        list_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        ttk.Label(list_frame, text="Variables Configuradas:").pack(anchor="w")
        self.vars_listbox = tk.Listbox(list_frame, bg="#f0f0f0")
        self.vars_listbox.pack(fill="both", expand=True)
        self.vars_listbox.bind('<Double-Button-1>', lambda e: self.edit_selected_variable()) # Doble click para editar

        # Botonera Lista
        list_btns = ttk.Frame(list_frame)
        list_btns.pack(fill="x", pady=5)
        
        ttk.Button(list_btns, text="✏ Editar Seleccionada", command=self.edit_selected_variable).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(list_btns, text="🗑 Borrar Seleccionada", command=self.delete_variable).pack(side="left", fill="x", expand=True, padx=2)

        # --- 3. CONTROL ---
        control_frame = ttk.LabelFrame(self.root, text="3. Control de Simulación", padding=10)
        control_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x")

        self.btn_start = ttk.Button(btn_frame, text="▶ INICIAR", command=self.start_simulation)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = ttk.Button(btn_frame, text="⏹ DETENER", command=self.stop_simulation, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.log_area = tk.Text(control_frame, height=8, bg="#222", fg="#0f0")
        self.log_area.pack(fill="both", expand=True, pady=5)

    # --- PANELES DINÁMICOS ---
    def _clear_options_frame(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.dynamic_widgets = {}

    def _update_dynamic_options(self, event=None):
        self._clear_options_frame()
        selection = self.combo_type.get()
        if selection == "Numérico": self._show_numeric_options()
        elif selection == "Texto": self._show_string_options()
        elif selection == "Lista": self._show_list_options()
        elif selection == "Fecha": self._show_date_options()

    def _show_numeric_options(self):
        ttk.Label(self.options_frame, text="Mínimo:").grid(row=0, column=0, sticky="w")
        min_entry = ttk.Entry(self.options_frame, width=10)
        min_entry.insert(0, "0")
        min_entry.grid(row=0, column=1, sticky="e")
        self.dynamic_widgets["min"] = min_entry

        ttk.Label(self.options_frame, text="Máximo:").grid(row=1, column=0, sticky="w")
        max_entry = ttk.Entry(self.options_frame, width=10)
        max_entry.insert(0, "100")
        max_entry.grid(row=1, column=1, sticky="e")
        self.dynamic_widgets["max"] = max_entry

        ttk.Label(self.options_frame, text="Estrategia:").grid(row=2, column=0, sticky="w", pady=5)
        strat = ttk.Combobox(self.options_frame, values=["random", "sequential", "constant"], width=12)
        strat.current(0)
        strat.grid(row=2, column=1, sticky="e")
        self.dynamic_widgets["strategy"] = strat

    def _show_string_options(self):
        ttk.Label(self.options_frame, text="Modo:").grid(row=0, column=0, sticky="w")
        mode_combo = ttk.Combobox(self.options_frame, values=["Aleatorio", "Regex (Patrón)"], state="readonly")
        mode_combo.current(0)
        mode_combo.grid(row=0, column=1, sticky="ew")
        self.dynamic_widgets["str_mode"] = mode_combo

        param_container = ttk.Frame(self.options_frame)
        param_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        def toggle_params(event=None):
            for widget in param_container.winfo_children(): widget.destroy()
            mode = mode_combo.get()
            if mode == "Regex (Patrón)":
                ttk.Label(param_container, text="Regex:").pack(anchor="w")
                entry = ttk.Entry(param_container)
                entry.insert(0, r"[A-Z]{3}-\d{3}")
                entry.pack(fill="x")
                self.dynamic_widgets["regex_pattern"] = entry
            else:
                f = ttk.Frame(param_container)
                f.pack(fill="x")
                min_l = ttk.Entry(f, width=5); min_l.insert(0, "5"); min_l.pack(side="left"); self.dynamic_widgets["min_len"] = min_l
                ttk.Label(f, text="-").pack(side="left")
                max_l = ttk.Entry(f, width=5); max_l.insert(0, "10"); max_l.pack(side="left"); self.dynamic_widgets["max_len"] = max_l
                
                self.dynamic_widgets["upper"] = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_container, text="A-Z", variable=self.dynamic_widgets["upper"]).pack(anchor="w")
                self.dynamic_widgets["nums"] = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_container, text="0-9", variable=self.dynamic_widgets["nums"]).pack(anchor="w")
                self.dynamic_widgets["syms"] = tk.BooleanVar(value=False)
                ttk.Checkbutton(param_container, text="Simbolos", variable=self.dynamic_widgets["syms"]).pack(anchor="w")

        mode_combo.bind("<<ComboboxSelected>>", toggle_params)
        toggle_params() # Init

    def _show_list_options(self):
        ttk.Label(self.options_frame, text="Valores (CSV):").pack(anchor="w")
        txt = tk.Text(self.options_frame, height=4, width=30)
        txt.insert("1.0", "A, B, C")
        txt.pack(fill="x")
        self.dynamic_widgets["values"] = txt
        
        ttk.Label(self.options_frame, text="Orden:").pack(anchor="w")
        strat = ttk.Combobox(self.options_frame, values=["random", "serial"])
        strat.current(0)
        strat.pack(fill="x")
        self.dynamic_widgets["strategy"] = strat

    def _show_date_options(self):
        ttk.Label(self.options_frame, text="Formato:").grid(row=0, column=0)
        fmt = ttk.Entry(self.options_frame); fmt.insert(0, "%Y-%m-%d %H:%M:%S"); fmt.grid(row=0, column=1)
        self.dynamic_widgets["format"] = fmt
        
        ttk.Label(self.options_frame, text="Estrategia:").grid(row=1, column=0)
        strat = ttk.Combobox(self.options_frame, values=["now", "increment", "fixed"])
        strat.current(0)
        strat.grid(row=1, column=1)
        self.dynamic_widgets["strategy"] = strat

    # --- LÓGICA DE GESTIÓN (AÑADIR / EDITAR / BORRAR) ---
    def add_or_update_variable(self):
        name = self.entry_var_name.get()
        v_type = self.combo_type.get()
        if not name: return

        try:
            var_obj = None
            desc = ""

            # 1. Construir Objeto
            if v_type == "Numérico":
                mn = float(self.dynamic_widgets["min"].get())
                mx = float(self.dynamic_widgets["max"].get())
                strat = self.dynamic_widgets["strategy"].get()
                var_obj = NumericVariable(name, mn, mx, strategy=strat)
                desc = f"{name} [Num: {mn}-{mx} | {strat}]"

            elif v_type == "Texto":
                mode = self.dynamic_widgets["str_mode"].get()
                if mode == "Regex (Patrón)":
                    pat = self.dynamic_widgets["regex_pattern"].get()
                    var_obj = StringVariable(name, strategy="regex", pattern=pat)
                    desc = f"{name} [Regex: {pat}]"
                else:
                    mn = int(self.dynamic_widgets["min_len"].get())
                    mx = int(self.dynamic_widgets["max_len"].get())
                    up = self.dynamic_widgets["upper"].get()
                    nu = self.dynamic_widgets["nums"].get()
                    sy = self.dynamic_widgets["syms"].get()
                    var_obj = StringVariable(name, strategy="random", min_len=mn, max_len=mx, 
                                           use_upper=up, use_nums=nu, use_sym=sy)
                    desc = f"{name} [Txt: {mn}-{mx}]"

            elif v_type == "Lista":
                raw = self.dynamic_widgets["values"].get("1.0", tk.END)
                vals = [x.strip() for x in raw.split(",") if x.strip()]
                strat = self.dynamic_widgets["strategy"].get()
                if not vals: raise ValueError("Lista vacía")
                var_obj = ListVariable(name, vals, strategy=strat)
                desc = f"{name} [Lista: {len(vals)} items | {strat}]"

            elif v_type == "Fecha":
                strat = self.dynamic_widgets["strategy"].get()
                fmt = self.dynamic_widgets["format"].get()
                var_obj = DateVariable(name, strategy=strat, date_format=fmt)
                desc = f"{name} [Fecha: {strat}]"

            # 2. Guardar (Nuevo o Actualización)
            if self.editing_index is None:
                # MODO NUEVO: Añadir al final
                self.added_variables.append(var_obj)
                self.vars_listbox.insert(tk.END, desc)
                self.entry_var_name.delete(0, tk.END) # Limpiar nombre solo si es nuevo
            else:
                # MODO EDICIÓN: Actualizar en el sitio
                self.added_variables[self.editing_index] = var_obj
                
                # --- CORRECCIÓN AQUÍ ---
                # Desbloqueamos la lista ANTES de intentar borrar/escribir
                self.vars_listbox.config(state="normal") 
                
                self.vars_listbox.delete(self.editing_index)
                self.vars_listbox.insert(self.editing_index, desc)
                
                self.cancel_edit() # Esto sale del modo edición

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def edit_selected_variable(self):
        sel = self.vars_listbox.curselection()
        if not sel: return
        
        index = sel[0]
        var = self.added_variables[index]
        self.editing_index = index # Marcamos que estamos editando
        
        # 1. Ajustar UI al modo edición
        self.btn_add_update.config(text="💾 Guardar Cambios")
        self.btn_cancel.config(state="normal")
        self.vars_listbox.config(state="disabled") # Bloquear lista mientras editas

        # 2. Rellenar Datos Comunes
        self.entry_var_name.delete(0, tk.END)
        self.entry_var_name.insert(0, var.name)
        
        # 3. Detectar Tipo y Rellenar
        if isinstance(var, NumericVariable):
            self.combo_type.set("Numérico")
            self._update_dynamic_options()
            self.dynamic_widgets["min"].delete(0, tk.END); self.dynamic_widgets["min"].insert(0, str(var.min_val))
            self.dynamic_widgets["max"].delete(0, tk.END); self.dynamic_widgets["max"].insert(0, str(var.max_val))
            self.dynamic_widgets["strategy"].set(var.strategy)
            
        elif isinstance(var, StringVariable):
            self.combo_type.set("Texto")
            self._update_dynamic_options()
            if var.strategy == "regex":
                self.dynamic_widgets["str_mode"].set("Regex (Patrón)")
                # Forzamos refresh del panel regex
                self.dynamic_widgets["str_mode"].event_generate("<<ComboboxSelected>>") 
                self.dynamic_widgets["regex_pattern"].delete(0, tk.END)
                self.dynamic_widgets["regex_pattern"].insert(0, var.pattern)
            else:
                self.dynamic_widgets["str_mode"].set("Aleatorio")
                self.dynamic_widgets["str_mode"].event_generate("<<ComboboxSelected>>")
                self.dynamic_widgets["min_len"].delete(0, tk.END); self.dynamic_widgets["min_len"].insert(0, str(var.min_len))
                self.dynamic_widgets["max_len"].delete(0, tk.END); self.dynamic_widgets["max_len"].insert(0, str(var.max_len))
                self.dynamic_widgets["upper"].set(var.use_upper)
                self.dynamic_widgets["nums"].set(var.use_nums)
                self.dynamic_widgets["syms"].set(var.use_sym)

        elif isinstance(var, ListVariable):
            self.combo_type.set("Lista")
            self._update_dynamic_options()
            text_val = ", ".join(var.values)
            self.dynamic_widgets["values"].delete("1.0", tk.END)
            self.dynamic_widgets["values"].insert("1.0", text_val)
            self.dynamic_widgets["strategy"].set(var.strategy)

        elif isinstance(var, DateVariable):
            self.combo_type.set("Fecha")
            self._update_dynamic_options()
            self.dynamic_widgets["format"].delete(0, tk.END)
            self.dynamic_widgets["format"].insert(0, var.date_format)
            self.dynamic_widgets["strategy"].set(var.strategy)

    def cancel_edit(self):
        """Salir del modo edición y limpiar"""
        self.editing_index = None
        self.btn_add_update.config(text="⬇ Añadir Variable")
        self.btn_cancel.config(state="disabled")
        self.vars_listbox.config(state="normal") # Desbloquear lista
        self.entry_var_name.delete(0, tk.END)
        self.combo_type.current(0)
        self._update_dynamic_options()

    def delete_variable(self):
        sel = self.vars_listbox.curselection()
        if sel:
            idx = sel[0]
            # Si estabamos editando justo esa, cancelamos edición
            if self.editing_index == idx:
                self.cancel_edit()
            
            self.vars_listbox.delete(idx)
            del self.added_variables[idx]
            
            # Ajustar indice de edición si borramos uno anterior
            if self.editing_index is not None and idx < self.editing_index:
                self.editing_index -= 1

    # --- RESTO DEL CÓDIGO (START/STOP/LOGS) ---
    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_simulation(self):
        if not self.added_variables: return
        freq = int(self.entry_freq.get())
        self.engine = NitrogenEngine(frequency_ms=freq)

        json_parts = []
        for v in self.added_variables:
            json_parts.append(f'"{v.name}": "{{{v.name}}}"')
        template_str = "{" + ", ".join(json_parts) + "}"
        self.log(f"--- Configuración Iniciada ---\nPlantilla: {template_str}")

        host = self.entry_host.get(); topic = self.entry_topic.get()
        connector = MqttConnector("GUI", template_str, host=host, topic=topic, on_message_callback=self.log)
        for v in self.added_variables: connector.add_variable(v)

        group = Group("MainGroup"); group.add_connector(connector)
        self.engine.add_group(group)
        self.engine_thread = threading.Thread(target=self.engine.start); self.engine_thread.daemon = True
        self.engine_thread.start()

        self.btn_start.config(state="disabled"); self.btn_stop.config(state="normal")

    def stop_simulation(self):
        if self.engine:
            self.engine.running = False
            self.log("--- Deteniendo... ---")
            self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NitrogenGUI(root)
        root.mainloop()
    except ImportError:
        print("Error: Instala tkinter")