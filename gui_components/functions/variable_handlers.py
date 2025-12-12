"""
Manejadores para añadir, editar y eliminar variables
"""
import tkinter as tk
from tkinter import messagebox
from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable, PointVariable, BooleanVariable


class VariableHandlers:
    def __init__(self, designer_panel):
        self.designer = designer_panel
        self.added_variables = []
        self.editing_index = None
        
        # Conectar botones
        self.designer.btn_add_update.config(command=self.add_or_update_variable)
        self.designer.btn_cancel.config(command=self.cancel_edit)
        self.designer.btn_edit.config(command=self.edit_selected_variable)
        self.designer.btn_delete.config(command=self.delete_variable)
        self.designer.vars_listbox.bind('<Double-Button-1>', lambda e: self.edit_selected_variable())
    
    def add_or_update_variable(self):
        """Añade o actualiza una variable"""
        name = self.designer.entry_var_name.get()
        if not name:
            return
        
        try:
            v_type = self.designer.combo_type.get()
            a_prob = float(self.designer.entry_anomaly_prob.get())
            a_val = self.designer.entry_anomaly_val.get()
            
            var, desc = self._create_variable(v_type, name, a_prob, a_val)
            
            if self.editing_index is None:
                self.added_variables.append(var)
                self.designer.vars_listbox.insert(tk.END, desc)
                self.designer.entry_var_name.delete(0, tk.END)
            else:
                self.added_variables[self.editing_index] = var
                self.designer.vars_listbox.config(state="normal")
                self.designer.vars_listbox.delete(self.editing_index)
                self.designer.vars_listbox.insert(self.editing_index, desc)
                self.cancel_edit()
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _create_variable(self, v_type, name, a_prob, a_val):
        """Crea una variable según su tipo"""
        dw = self.designer.dynamic_widgets
        
        if v_type == "Numérico":
            mn = float(dw["min"].get())
            mx = float(dw["max"].get())
            strat = dw["strategy"].get()
            step = float(dw["step"].get())
            
            try:
                val_anom = float(a_val)
            except:
                val_anom = a_val
            
            var = NumericVariable(name, mn, mx, strategy=strat, step=step,
                                  anomaly_prob=a_prob, anomaly_value=val_anom)
            desc = f"{name} [Num: {strat} | Step {step}]"
        
        elif v_type == "Texto":
            mode = dw["str_mode"].get()
            
            if mode == "Regex (Patrón)":
                pat = dw["regex_pattern"].get()
                var = StringVariable(name, strategy="regex", pattern=pat,
                                     anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [Regex: {pat}]"
            else:
                mn = int(dw["min_len"].get())
                mx = int(dw["max_len"].get())
                up = dw["upper"].get()
                nu = dw["nums"].get()
                sy = dw["syms"].get()
                
                var = StringVariable(name, strategy="random", min_len=mn, max_len=mx,
                                     use_upper=up, use_nums=nu, use_sym=sy,
                                     anomaly_prob=a_prob, anomaly_value=a_val)
                desc = f"{name} [Txt: {mn}-{mx}]"
            
            if a_prob > 0:
                desc += f" | ⚠ {a_prob}%"
        
        elif v_type == "Lista":
            vals = dw["vals"].get("1.0", tk.END).replace("\n", "").split(",")
            st = dw["strat"].get()
            var = ListVariable(name, vals, strategy=st, anomaly_prob=a_prob, anomaly_value=a_val)
            desc = f"{name} [List]"
        
        elif v_type == "Fecha":
            fmt = dw["fmt"].get()
            st = dw["strat"].get()
            var = DateVariable(name, strategy=st, date_format=fmt, anomaly_prob=a_prob, anomaly_value=a_val)
            desc = f"{name} [Date]"
        
        elif v_type == "Punto":
            dim_str = dw["dim"].get()
            dim = 2 if dim_str == "2D" else 3
            
            xr = (float(dw["x_min"].get()), float(dw["x_max"].get()))
            yr = (float(dw["y_min"].get()), float(dw["y_max"].get()))
            zr = (float(dw["z_min"].get()), float(dw["z_max"].get()))
            
            st = dw["strat"].get()
            step = float(dw["step"].get())
            
            var = PointVariable(name, dimension=dim, x_range=xr, y_range=yr, z_range=zr,
                                strategy=st, step=step, anomaly_prob=a_prob, anomaly_value=a_val)
            desc = f"{name} [Punto {dim}D]"
        
        elif v_type == "Booleano":
            strat = dw["strat"].get()
            prob = 50.0
            init_val = True
            
            if strat == "random":
                prob = float(dw["true_prob"].get())
            else:
                init_val = (dw["init_val"].get() == "True")
            
            var = BooleanVariable(name, strategy=strat, true_prob=prob, initial_value=init_val,
                                  anomaly_prob=a_prob, anomaly_value=a_val)
            
            if strat == "random":
                desc = f"{name} [Bool: {prob}% True]"
            else:
                desc = f"{name} [Bool: {strat}]"
        
        return var, desc
    
    def edit_selected_variable(self):
        """Edita la variable seleccionada"""
        sel = self.designer.vars_listbox.curselection()
        if not sel:
            return
        
        index = sel[0]
        var = self.added_variables[index]
        self.editing_index = index
        
        # Ajustar UI
        self.designer.btn_add_update.config(text="💾 Guardar Cambios")
        self.designer.btn_cancel.config(state="normal")
        self.designer.vars_listbox.config(state="disabled")
        
        # Rellenar campos comunes
        self.designer.entry_var_name.delete(0, tk.END)
        self.designer.entry_var_name.insert(0, var.name)
        
        self.designer.entry_anomaly_prob.delete(0, tk.END)
        self.designer.entry_anomaly_prob.insert(0, str(var.anomaly_prob))
        
        self.designer.entry_anomaly_val.delete(0, tk.END)
        self.designer.entry_anomaly_val.insert(0, str(var.anomaly_value))
        
        # Rellenar según tipo
        self._fill_variable_fields(var)
    
    def _fill_variable_fields(self, var):
        """Rellena los campos según el tipo de variable"""
        dw = self.designer.dynamic_widgets
        
        if isinstance(var, NumericVariable):
            self.designer.combo_type.set("Numérico")
            self.designer._update_dynamic_options()
            
            dw["min"].delete(0, tk.END)
            dw["min"].insert(0, str(var.min_val))
            dw["max"].delete(0, tk.END)
            dw["max"].insert(0, str(var.max_val))
            dw["step"].delete(0, tk.END)
            dw["step"].insert(0, str(var.step))
            dw["strategy"].set(var.strategy)
        
        elif isinstance(var, StringVariable):
            self.designer.combo_type.set("Texto")
            self.designer._update_dynamic_options()
            
            if var.strategy == "regex":
                dw["str_mode"].set("Regex (Patrón)")
                dw["str_mode"].event_generate("<<ComboboxSelected>>")
                self.designer.root.update_idletasks()
                
                dw["regex_pattern"].delete(0, tk.END)
                dw["regex_pattern"].insert(0, var.pattern)
            else:
                dw["str_mode"].set("Aleatorio")
                dw["str_mode"].event_generate("<<ComboboxSelected>>")
                self.designer.root.update_idletasks()
                
                dw["min_len"].delete(0, tk.END)
                dw["min_len"].insert(0, str(var.min_len))
                dw["max_len"].delete(0, tk.END)
                dw["max_len"].insert(0, str(var.max_len))
                dw["upper"].set(var.use_upper)
                dw["nums"].set(var.use_nums)
                dw["syms"].set(var.use_sym)
        
        elif isinstance(var, ListVariable):
            self.designer.combo_type.set("Lista")
            self.designer._update_dynamic_options()
            
            text_val = ", ".join(var.values)
            dw["vals"].delete("1.0", tk.END)
            dw["vals"].insert("1.0", text_val)
            dw["strat"].set(var.strategy)
        
        elif isinstance(var, DateVariable):
            self.designer.combo_type.set("Fecha")
            self.designer._update_dynamic_options()
            
            dw["fmt"].delete(0, tk.END)
            dw["fmt"].insert(0, var.date_format)
            dw["strat"].set(var.strategy)
        
        elif isinstance(var, PointVariable):
            self.designer.combo_type.set("Punto")
            self.designer._update_dynamic_options()
            
            dim_str = "3D" if var.dimension == 3 else "2D"
            dw["dim"].set(dim_str)
            dw["dim"].event_generate("<<ComboboxSelected>>")
            self.designer.root.update_idletasks()
            
            dw["strat"].set(var.strategy)
            dw["step"].delete(0, tk.END)
            dw["step"].insert(0, str(var.step))
            
            dw["x_min"].delete(0, tk.END)
            dw["x_min"].insert(0, str(var.x_range[0]))
            dw["x_max"].delete(0, tk.END)
            dw["x_max"].insert(0, str(var.x_range[1]))
            
            dw["y_min"].delete(0, tk.END)
            dw["y_min"].insert(0, str(var.y_range[0]))
            dw["y_max"].delete(0, tk.END)
            dw["y_max"].insert(0, str(var.y_range[1]))
            
            dw["z_min"].delete(0, tk.END)
            dw["z_min"].insert(0, str(var.z_range[0]))
            dw["z_max"].delete(0, tk.END)
            dw["z_max"].insert(0, str(var.z_range[1]))
        
        elif isinstance(var, BooleanVariable):
            self.designer.combo_type.set("Booleano")
            self.designer._update_dynamic_options()
            
            dw["strat"].set(var.strategy)
            dw["strat"].event_generate("<<ComboboxSelected>>")
            self.designer.root.update_idletasks()
            
            if var.strategy == "random":
                dw["true_prob"].delete(0, tk.END)
                dw["true_prob"].insert(0, str(var.true_prob))
            else:
                val_str = "True" if var.current_value else "False"
                dw["init_val"].set(val_str)
    
    def cancel_edit(self):
        """Cancela la edición"""
        self.editing_index = None
        self.designer.btn_add_update.config(text="⬇ Añadir Variable")
        self.designer.btn_cancel.config(state="disabled")
        self.designer.vars_listbox.config(state="normal")
        self.designer.entry_var_name.delete(0, tk.END)
    
    def delete_variable(self):
        """Elimina la variable seleccionada"""
        sel = self.designer.vars_listbox.curselection()
        if sel:
            self.designer.vars_listbox.delete(sel[0])
            del self.added_variables[sel[0]]
