"""
Opciones dinámicas para cada tipo de variable
"""
import tkinter as tk
from tkinter import ttk

class VariableOptions:
    def __init__(self, options_frame, dynamic_widgets, root):
        self.options_frame = options_frame
        self.dynamic_widgets = dynamic_widgets
        self.root = root
        self.current_sub_frame = None  # Referencia para limpiar sub-opciones
    
    def show_options(self, var_type):
        """Muestra las opciones según el tipo de variable"""
        if var_type == "Numérico":
            self._show_numeric_options()
        elif var_type == "Texto":
            self._show_string_options()
        elif var_type == "Lista":
            self._show_list_options()
        elif var_type == "Fecha":
            self._show_date_options()
        elif var_type == "Punto":
            self._show_point_options()
        elif var_type == "Booleano":
            self._show_boolean_options()
    
    # --- MÉTODOS AUXILIARES PARA LIMPIAR SUB-FRAMES ---
    def _clear_sub_frame(self):
        if self.current_sub_frame:
            for widget in self.current_sub_frame.winfo_children():
                widget.destroy()

    # --- NUMÉRICO ---
    def _show_numeric_options(self):
        ttk.Label(self.options_frame, text="Rango (Min-Max):").pack()
        f = ttk.Frame(self.options_frame)
        f.pack()
        e1 = ttk.Entry(f, width=8)
        e1.insert(0, "0")
        e1.pack(side="left")
        ttk.Label(f, text="-").pack(side="left")
        e2 = ttk.Entry(f, width=8)
        e2.insert(0, "100")
        e2.pack(side="left")
        self.dynamic_widgets["min"] = e1
        self.dynamic_widgets["max"] = e2
        
        ttk.Label(self.options_frame, text="Estrategia:").pack()
        c = ttk.Combobox(self.options_frame, values=["random", "sequential", "constant", "trend"])
        c.current(0)
        c.pack()
        self.dynamic_widgets["strategy"] = c
        
        ttk.Label(self.options_frame, text="Paso / Variación (Step):").pack()
        e_s = ttk.Entry(self.options_frame, width=8)
        e_s.insert(0, "1")
        e_s.pack()
        self.dynamic_widgets["step"] = e_s
    
    # --- TEXTO (STRING) ---
    def _show_string_options(self):
        ttk.Label(self.options_frame, text="Modo:").pack(anchor="w")
        mode_combo = ttk.Combobox(
            self.options_frame, 
            values=["Aleatorio", "Regex (Patrón)"], 
            state="readonly"
        )
        mode_combo.current(0)
        mode_combo.pack(fill="x", pady=2)
        self.dynamic_widgets["str_mode"] = mode_combo
        
        # Contenedor para parámetros cambiantes
        self.current_sub_frame = ttk.Frame(self.options_frame)
        self.current_sub_frame.pack(fill="both", expand=True, pady=5)
        
        mode_combo.bind("<<ComboboxSelected>>", self.update_string_params)
        self.update_string_params() # Inicializar

    def update_string_params(self, event=None):
        self._clear_sub_frame()
        mode = self.dynamic_widgets["str_mode"].get()
        
        if mode == "Regex (Patrón)":
            ttk.Label(self.current_sub_frame, text="Expresión Regular:").pack(anchor="w")
            entry_regex = ttk.Entry(self.current_sub_frame)
            entry_regex.insert(0, r"[A-Z]{3}-\d{3}")
            entry_regex.pack(fill="x")
            self.dynamic_widgets["regex_pattern"] = entry_regex
            ttk.Label(self.current_sub_frame, text=r"Ej: \d{4}[A-Z] (Matrícula)", font=("Arial", 8)).pack(anchor="w")
        else:
            f = ttk.Frame(self.current_sub_frame)
            f.pack(fill="x")
            ttk.Label(f, text="Min Len:").pack(side="left")
            min_l = ttk.Entry(f, width=5)
            min_l.insert(0, "5")
            min_l.pack(side="left", padx=2)
            self.dynamic_widgets["min_len"] = min_l
            
            ttk.Label(f, text="Max Len:").pack(side="left")
            max_l = ttk.Entry(f, width=5)
            max_l.insert(0, "10")
            max_l.pack(side="left", padx=2)
            self.dynamic_widgets["max_len"] = max_l
            
            self.dynamic_widgets["upper"] = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.current_sub_frame, text="A-Z", variable=self.dynamic_widgets["upper"]).pack(anchor="w")
            self.dynamic_widgets["nums"] = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.current_sub_frame, text="0-9", variable=self.dynamic_widgets["nums"]).pack(anchor="w")
            self.dynamic_widgets["syms"] = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.current_sub_frame, text="Simbolos", variable=self.dynamic_widgets["syms"]).pack(anchor="w")

    # --- LISTA ---
    def _show_list_options(self):
        ttk.Label(self.options_frame, text="Valores (CSV):").pack()
        t = tk.Text(self.options_frame, height=3, width=25)
        t.insert("1.0", "ON,OFF")
        t.pack()
        self.dynamic_widgets["vals"] = t
        c = ttk.Combobox(self.options_frame, values=["random", "serial"])
        c.current(0)
        c.pack()
        self.dynamic_widgets["strat"] = c
    
    # --- FECHA ---
    def _show_date_options(self):
        ttk.Label(self.options_frame, text="Formato:").pack()
        e = ttk.Entry(self.options_frame)
        e.insert(0, "%H:%M:%S")
        e.pack()
        self.dynamic_widgets["fmt"] = e
        c = ttk.Combobox(self.options_frame, values=["now", "increment"])
        c.current(0)
        c.pack()
        self.dynamic_widgets["strat"] = c
    
    # --- PUNTO ---
    def _show_point_options(self):
        ttk.Label(self.options_frame, text="Dimensión:").pack()
        c_dim = ttk.Combobox(self.options_frame, values=["2D", "3D"], state="readonly")
        c_dim.current(1)
        c_dim.pack()
        self.dynamic_widgets["dim"] = c_dim
        
        self.current_sub_frame = ttk.Frame(self.options_frame)
        self.current_sub_frame.pack(pady=5)
        
        # Guardamos referencias fijas para X, Y, Z aunque se oculten
        # Esto es un cambio respecto al original para evitar errores, 
        # pero para mantener la lógica visual, usaremos la lógica de grid_remove
        
        # Re-creamos la estructura
        # X
        ttk.Label(self.current_sub_frame, text="X (Min-Max):").grid(row=0, column=0)
        ex1 = ttk.Entry(self.current_sub_frame, width=5); ex1.insert(0, "0"); ex1.grid(row=0, column=1)
        ex2 = ttk.Entry(self.current_sub_frame, width=5); ex2.insert(0, "100"); ex2.grid(row=0, column=2)
        self.dynamic_widgets["x_min"] = ex1; self.dynamic_widgets["x_max"] = ex2
        
        # Y
        ttk.Label(self.current_sub_frame, text="Y (Min-Max):").grid(row=1, column=0)
        ey1 = ttk.Entry(self.current_sub_frame, width=5); ey1.insert(0, "0"); ey1.grid(row=1, column=1)
        ey2 = ttk.Entry(self.current_sub_frame, width=5); ey2.insert(0, "100"); ey2.grid(row=1, column=2)
        self.dynamic_widgets["y_min"] = ey1; self.dynamic_widgets["y_max"] = ey2
        
        # Z
        self.z_label = ttk.Label(self.current_sub_frame, text="Z (Min-Max):")
        self.z_label.grid(row=2, column=0)
        ez1 = ttk.Entry(self.current_sub_frame, width=5); ez1.insert(0, "0"); ez1.grid(row=2, column=1)
        ez2 = ttk.Entry(self.current_sub_frame, width=5); ez2.insert(0, "100"); ez2.grid(row=2, column=2)
        self.dynamic_widgets["z_min"] = ez1; self.dynamic_widgets["z_max"] = ez2
        
        c_dim.bind("<<ComboboxSelected>>", self.update_point_params)
        self.update_point_params() # Init
        
        ttk.Label(self.options_frame, text="Estrategia:").pack()
        c_st = ttk.Combobox(self.options_frame, values=["random", "trend"])
        c_st.current(0)
        c_st.pack()
        self.dynamic_widgets["strat"] = c_st
        
        ttk.Label(self.options_frame, text="Paso (Speed):").pack()
        e_sp = ttk.Entry(self.options_frame, width=5)
        e_sp.insert(0, "1.0")
        e_sp.pack()
        self.dynamic_widgets["step"] = e_sp

    def update_point_params(self, event=None):
        dim = self.dynamic_widgets["dim"].get()
        if dim == "2D":
            self.z_label.grid_remove()
            self.dynamic_widgets["z_min"].grid_remove()
            self.dynamic_widgets["z_max"].grid_remove()
        else:
            self.z_label.grid()
            self.dynamic_widgets["z_min"].grid()
            self.dynamic_widgets["z_max"].grid()

    # --- BOOLEANO ---
    def _show_boolean_options(self):
        ttk.Label(self.options_frame, text="Estrategia:").pack(anchor="w")
        c_strat = ttk.Combobox(
            self.options_frame, 
            values=["random", "alternating", "constant"], 
            state="readonly"
        )
        c_strat.current(0)
        c_strat.pack(fill="x", pady=2)
        self.dynamic_widgets["strat"] = c_strat
        
        self.current_sub_frame = ttk.Frame(self.options_frame)
        self.current_sub_frame.pack(fill="x", pady=5)
        
        c_strat.bind("<<ComboboxSelected>>", self.update_boolean_params)
        self.update_boolean_params()

    def update_boolean_params(self, event=None):
        self._clear_sub_frame()
        strat = self.dynamic_widgets["strat"].get()
        
        if strat == "random":
            ttk.Label(self.current_sub_frame, text="Probabilidad True (%):").pack(side="left")
            e_prob = ttk.Entry(self.current_sub_frame, width=5)
            e_prob.insert(0, "50")
            e_prob.pack(side="left", padx=5)
            self.dynamic_widgets["true_prob"] = e_prob
        else:
            lbl = "Valor Fijo:" if strat == "constant" else "Valor Inicial:"
            ttk.Label(self.current_sub_frame, text=lbl).pack(side="left")
            c_val = ttk.Combobox(self.current_sub_frame, values=["True", "False"], state="readonly", width=8)
            c_val.current(0)
            c_val.pack(side="left", padx=5)
            self.dynamic_widgets["init_val"] = c_val