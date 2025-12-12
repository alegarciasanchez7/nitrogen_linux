"""
Panel de diseño de variables con scroll
"""
import tkinter as tk
from tkinter import ttk
from ..functions.variable_options import VariableOptions


class VariableDesignerPanel:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.dynamic_widgets = {}
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="2. Diseñador de Variables", padding=10)
        
        self._create_scrollable_form()
        self._create_variable_list()
        
        # Módulo de opciones dinámicas
        self.var_options = VariableOptions(self.options_frame, self.dynamic_widgets, root)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def _create_scrollable_form(self):
        """Crea el formulario con scroll en el lado izquierdo"""
        left_container = ttk.Frame(self.frame, width=400)
        left_container.pack(side="left", fill="y", padx=5)
        
        # Elevar el contenedor para que esté por encima
        left_container.lift()
        
        canvas = tk.Canvas(left_container, width=370, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Centrar el contenido dentro del canvas
        canvas.create_window((185, 0), window=self.scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear formulario
        self._create_form(self.scrollable_frame)
    
    def _create_form(self, form_frame):
        """Crea los campos del formulario"""
        # Nombre Variable
        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame)
        self.entry_var_name.pack(fill="x", pady=2)
        
        # Tipo
        ttk.Label(form_frame, text="Tipo:").pack(anchor="w", pady=(5, 0))
        self.combo_type = ttk.Combobox(
            form_frame, 
            state="readonly", 
            values=["Numérico", "Texto", "Lista", "Fecha", "Punto", "Booleano"]
        )
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", self._update_dynamic_options)
        
        # Frame de opciones dinámicas
        self.options_frame = ttk.LabelFrame(form_frame, text="Parámetros", padding=5)
        self.options_frame.pack(fill="x", pady=5)
        
        # Panel Anomalía
        self._create_anomaly_panel(form_frame)
        
        # Botones
        self._create_buttons(form_frame)
    
    def _create_anomaly_panel(self, parent):
        """Crea el panel de anomalías"""
        anomaly_frame = ttk.LabelFrame(parent, text="Anomalías (Fallos)", padding=5)
        anomaly_frame.pack(fill="x", pady=5)
        
        ttk.Label(anomaly_frame, text="Probabilidad (%):").grid(row=0, column=0)
        self.entry_anomaly_prob = ttk.Entry(anomaly_frame, width=8)
        self.entry_anomaly_prob.insert(0, "0")
        self.entry_anomaly_prob.grid(row=0, column=1)
        
        ttk.Label(anomaly_frame, text="Valor:").grid(row=0, column=2)
        self.entry_anomaly_val = ttk.Entry(anomaly_frame, width=10)
        self.entry_anomaly_val.insert(0, "ERR")
        self.entry_anomaly_val.grid(row=0, column=3)
    
    def _create_buttons(self, parent):
        """Crea los botones de acción"""
        btn_box = ttk.Frame(parent)
        btn_box.pack(fill="x", pady=10)
        
        self.btn_add_update = ttk.Button(
            btn_box, 
            text="⬇ Añadir Variable"
        )
        self.btn_add_update.pack(side="left", fill="x", expand=True)
        
        self.btn_cancel = ttk.Button(
            btn_box, 
            text="Cancelar", 
            state="disabled"
        )
        self.btn_cancel.pack(side="right")
    
    def _create_variable_list(self):
        """Crea la lista de variables en el lado derecho"""
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Elevar este frame por encima del formulario
        list_frame.lift()
        
        self.vars_listbox = tk.Listbox(list_frame, bg="#f0f0f0")
        self.vars_listbox.pack(fill="both", expand=True)
        
        l_btns = ttk.Frame(list_frame)
        l_btns.pack(fill="x", pady=5)
        
        self.btn_edit = ttk.Button(l_btns, text="Editar")
        self.btn_edit.pack(side="left", fill="x", expand=True)
        
        self.btn_delete = ttk.Button(l_btns, text="Borrar")
        self.btn_delete.pack(side="left", fill="x", expand=True)
    
    def _update_dynamic_options(self, event=None):
        """Actualiza las opciones dinámicas según el tipo seleccionado"""
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.dynamic_widgets = {}
        
        sel = self.combo_type.get()
        self.var_options.dynamic_widgets = self.dynamic_widgets
        self.var_options.show_options(sel)
