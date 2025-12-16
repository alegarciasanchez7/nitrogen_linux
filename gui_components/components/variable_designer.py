"""
Panel de diseño de variables con scroll
"""
import tkinter as tk
from tkinter import ttk
from ..functions.variable_options import VariableOptions


class VariableDesignerPanel:
    def __init__(self, parent, root, on_event_update_callback):
        self.parent = parent
        self.root = root
        self.on_event_update = on_event_update_callback # Para notificar a la lista que refresque nombre/frec
        self.current_event = None
        self.dynamic_widgets = {}
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="3. Diseñador de Variables (Evento Seleccionado)", padding=10)
        
        # --- CABECERA DE CONFIGURACIÓN DE EVENTO (Nombre y Frec) ---
        self.header_frame = ttk.Frame(self.frame)

        ttk.Label(self.header_frame, text="Nombre Evento:").pack(side="left")
        self.entry_evt_name = ttk.Entry(self.header_frame)
        self.entry_evt_name.pack(side="left", padx=5)
        self.entry_evt_name.bind("<KeyRelease>", self._save_header_changes)
        
        ttk.Label(self.header_frame, text="Freq (ms):").pack(side="left")
        self.entry_evt_freq = ttk.Entry(self.header_frame, width=8)
        self.entry_evt_freq.pack(side="left", padx=5)
        self.entry_evt_freq.bind("<KeyRelease>", self._save_header_changes)
        # -----------------------------------------

        # Frame de Contenido (Formulario y Lista)
        self.content_frame = ttk.Frame(self.frame)
        
        self._create_scrollable_form(self.content_frame)
        self._create_variable_list(self.content_frame)   
        
        self.var_options = VariableOptions(self.options_frame, self.dynamic_widgets, root)
        
        # Iniciar todo oculto
        self.load_event(None)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def _create_scrollable_form(self, parent_frame):
        """Crea el formulario con scroll en el lado izquierdo"""
        left_container = ttk.Frame(parent_frame, width=400)
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
    
    def _create_variable_list(self, parent_frame):
        """Crea la lista de variables en el lado derecho"""
        list_frame = ttk.Frame(parent_frame)
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

    def load_event(self, event_config):
        """Carga un evento en el diseñador o limpia la vista si es None"""
        self.current_event = event_config
        
        if event_config is None:
            # OCULTAR
            self.header_frame.pack_forget()
            self.content_frame.pack_forget()
            
            # Limpiar datos residuales
            self._clear_header()
            self.vars_listbox.delete(0, tk.END)
            return

        # MOSTRAR
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.content_frame.pack(fill="both", expand=True)
        
        # Habilitar inputs
        self.entry_evt_name.config(state="normal")
        self.entry_evt_freq.config(state="normal")
        
        # Cargar Cabecera
        self.entry_evt_name.delete(0, tk.END)
        self.entry_evt_name.insert(0, event_config.name)
        self.entry_evt_freq.delete(0, tk.END)
        self.entry_evt_freq.insert(0, str(event_config.frequency))
        
        # Cargar Lista de Variables
        self.vars_listbox.delete(0, tk.END)
        for var in event_config.variables:
            # Construimos una descripción simple
            self.vars_listbox.insert(tk.END, f"{var.name} [{type(var).__name__}]")

    def _save_header_changes(self, event=None):
        """Guarda cambios de Nombre/Frec al instante"""
        if not self.current_event: return
        
        self.current_event.name = self.entry_evt_name.get()
        try:
            self.current_event.frequency = int(self.entry_evt_freq.get())
        except:
            pass # Ignorar enteros inválidos mientras se escribe
            
        if self.on_event_update:
            self.on_event_update()

    def _clear_header(self):
        """Limpia los campos de cabecera de forma segura"""
        self.entry_evt_name.config(state="normal")
        self.entry_evt_name.delete(0, tk.END)
        
        self.entry_evt_freq.config(state="normal")
        self.entry_evt_freq.delete(0, tk.END)