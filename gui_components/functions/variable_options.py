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
        
        param_container = ttk.Frame(self.options_frame)
        param_container.pack(fill="both", expand=True, pady=5)
        
        def toggle_params(event=None):
            for widget in param_container.winfo_children():
                widget.destroy()
            
            mode = mode_combo.get()
            
            if mode == "Regex (Patrón)":
                ttk.Label(param_container, text="Expresión Regular:").pack(anchor="w")
                entry_regex = ttk.Entry(param_container)
                entry_regex.insert(0, r"[A-Z]{3}-\d{3}")
                entry_regex.pack(fill="x")
                self.dynamic_widgets["regex_pattern"] = entry_regex
                
                ttk.Label(param_container, text=r"Ej: \d{4}[A-Z] (Matrícula)", font=("Arial", 8)).pack(anchor="w")
            else:
                f = ttk.Frame(param_container)
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
                ttk.Checkbutton(param_container, text="A-Z", variable=self.dynamic_widgets["upper"]).pack(anchor="w")
                self.dynamic_widgets["nums"] = tk.BooleanVar(value=True)
                ttk.Checkbutton(param_container, text="0-9", variable=self.dynamic_widgets["nums"]).pack(anchor="w")
                self.dynamic_widgets["syms"] = tk.BooleanVar(value=False)
                ttk.Checkbutton(param_container, text="Simbolos", variable=self.dynamic_widgets["syms"]).pack(anchor="w")
        
        mode_combo.bind("<<ComboboxSelected>>", toggle_params)
        toggle_params()
    
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
    
    def _show_point_options(self):
        ttk.Label(self.options_frame, text="Dimensión:").pack()
        c_dim = ttk.Combobox(self.options_frame, values=["2D", "3D"], state="readonly")
        c_dim.current(1)
        c_dim.pack()
        self.dynamic_widgets["dim"] = c_dim
        
        f_r = ttk.Frame(self.options_frame)
        f_r.pack(pady=5)
        
        # X
        ttk.Label(f_r, text="X (Min-Max):").grid(row=0, column=0)
        ex1 = ttk.Entry(f_r, width=5)
        ex1.insert(0, "0")
        ex1.grid(row=0, column=1)
        ex2 = ttk.Entry(f_r, width=5)
        ex2.insert(0, "100")
        ex2.grid(row=0, column=2)
        self.dynamic_widgets["x_min"] = ex1
        self.dynamic_widgets["x_max"] = ex2
        
        # Y
        ttk.Label(f_r, text="Y (Min-Max):").grid(row=1, column=0)
        ey1 = ttk.Entry(f_r, width=5)
        ey1.insert(0, "0")
        ey1.grid(row=1, column=1)
        ey2 = ttk.Entry(f_r, width=5)
        ey2.insert(0, "100")
        ey2.grid(row=1, column=2)
        self.dynamic_widgets["y_min"] = ey1
        self.dynamic_widgets["y_max"] = ey2
        
        # Z
        z_label = ttk.Label(f_r, text="Z (Min-Max):")
        z_label.grid(row=2, column=0)
        ez1 = ttk.Entry(f_r, width=5)
        ez1.insert(0, "0")
        ez1.grid(row=2, column=1)
        ez2 = ttk.Entry(f_r, width=5)
        ez2.insert(0, "100")
        ez2.grid(row=2, column=2)
        self.dynamic_widgets["z_min"] = ez1
        self.dynamic_widgets["z_max"] = ez2
        self.dynamic_widgets["z_label"] = z_label
        
        def toggle_z_axis(event=None):
            dim = c_dim.get()
            if dim == "2D":
                z_label.grid_remove()
                ez1.grid_remove()
                ez2.grid_remove()
            else:
                z_label.grid()
                ez1.grid()
                ez2.grid()
        
        c_dim.bind("<<ComboboxSelected>>", toggle_z_axis)
        toggle_z_axis()
        
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
        
        sub_frame = ttk.Frame(self.options_frame)
        sub_frame.pack(fill="x", pady=5)
        
        def update_sub_options(event=None):
            for w in sub_frame.winfo_children():
                w.destroy()
            strat = c_strat.get()
            
            if strat == "random":
                ttk.Label(sub_frame, text="Probabilidad True (%):").pack(side="left")
                e_prob = ttk.Entry(sub_frame, width=5)
                e_prob.insert(0, "50")
                e_prob.pack(side="left", padx=5)
                self.dynamic_widgets["true_prob"] = e_prob
            else:
                lbl = "Valor Fijo:" if strat == "constant" else "Valor Inicial:"
                ttk.Label(sub_frame, text=lbl).pack(side="left")
                c_val = ttk.Combobox(sub_frame, values=["True", "False"], state="readonly", width=8)
                c_val.current(0)
                c_val.pack(side="left", padx=5)
                self.dynamic_widgets["init_val"] = c_val
        
        c_strat.bind("<<ComboboxSelected>>", update_sub_options)
        update_sub_options()
