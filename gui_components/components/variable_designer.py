"""
Panel de diseño de variables con scroll y reordenamiento
"""
import tkinter as tk
from tkinter import ttk
from ..functions.variable_options import VariableOptions

class VariableDesignerPanel:
    def __init__(self, parent, root, on_event_update_callback):
        self.parent = parent
        self.root = root
        self.on_event_update = on_event_update_callback
        self.current_event = None
        self.dynamic_widgets = {}
        
        # Estado de la lista
        self.selected_index = None
        self.on_var_double_click = None # Callback para edición
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="3. Diseñador de Variables (Evento Seleccionado)", padding=10)
        
        # --- CABECERA ---
        self.header_frame = ttk.Frame(self.frame)
        
        ttk.Label(self.header_frame, text="Nombre Evento:").pack(side="left")
        self.entry_evt_name = ttk.Entry(self.header_frame)
        self.entry_evt_name.pack(side="left", padx=5)
        self.entry_evt_name.bind("<KeyRelease>", self._save_header_changes)
        
        ttk.Label(self.header_frame, text="Freq (ms):").pack(side="left")
        self.entry_evt_freq = ttk.Entry(self.header_frame, width=8)
        self.entry_evt_freq.pack(side="left", padx=5)
        self.entry_evt_freq.bind("<KeyRelease>", self._save_header_changes)
        
        # Frame de Contenido
        self.content_frame = ttk.Frame(self.frame)
        
        self._create_scrollable_form(self.content_frame)
        self._create_variable_list(self.content_frame) # Lista personalizada
        
        self.var_options = VariableOptions(self.options_frame, self.dynamic_widgets, root)
        
        # Iniciar oculto
        self.load_event(None)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def _create_scrollable_form(self, parent_frame):
        """Crea el formulario con scroll (Izquierda)"""
        left_container = ttk.Frame(parent_frame, width=400)
        left_container.pack(side="left", fill="y", padx=5)
        left_container.lift()
        
        canvas = tk.Canvas(left_container, width=370, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((185, 0), window=self.scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._create_form(self.scrollable_frame)
    
    def _create_form(self, form_frame):
        """Campos del formulario"""
        ttk.Label(form_frame, text="Nombre Variable:").pack(anchor="w")
        self.entry_var_name = ttk.Entry(form_frame)
        self.entry_var_name.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Tipo:").pack(anchor="w", pady=(5, 0))
        self.combo_type = ttk.Combobox(form_frame, state="readonly", values=["Numérico", "Texto", "Lista", "Fecha", "Punto", "Booleano"])
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", self._update_dynamic_options)
        
        self.options_frame = ttk.LabelFrame(form_frame, text="Parámetros", padding=5)
        self.options_frame.pack(fill="x", pady=5)
        
        self._create_anomaly_panel(form_frame)
        self._create_buttons(form_frame)
    
    def _create_anomaly_panel(self, parent):
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
        btn_box = ttk.Frame(parent)
        btn_box.pack(fill="x", pady=10)
        self.btn_add_update = ttk.Button(btn_box, text="⬇ Añadir Variable")
        self.btn_add_update.pack(side="left", fill="x", expand=True)
        self.btn_cancel = ttk.Button(btn_box, text="Cancelar", state="disabled")
        self.btn_cancel.pack(side="right")

    def _create_variable_list(self, parent_frame):
        """Crea la lista personalizada con botones de orden (Derecha)"""
        right_container = ttk.Frame(parent_frame)
        right_container.pack(side="right", fill="both", expand=True, padx=5)
        right_container.lift()
        
        # --- Contenedor Scrollable para la lista ---
        list_frame_container = ttk.Frame(right_container)
        list_frame_container.pack(side="top", fill="both", expand=True)
        
        canvas = tk.Canvas(list_frame_container, bg="white", highlightthickness=1, highlightbackground="#ccc")
        scrollbar = ttk.Scrollbar(list_frame_container, orient="vertical", command=canvas.yview)
        
        self.vars_scroll_frame = ttk.Frame(canvas)
        self.vars_scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.vars_scroll_frame, anchor="nw", width=350) # Width fijo aprox para ajuste
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind para ajustar el ancho de las filas al redimensionar
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(canvas.find_all()[0], width=e.width))

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # --- Botones de acción inferiores ---
        l_btns = ttk.Frame(right_container)
        l_btns.pack(fill="x", pady=5)
        
        self.btn_edit = ttk.Button(l_btns, text="Editar")
        self.btn_edit.pack(side="left", fill="x", expand=True)
        
        self.btn_delete = ttk.Button(l_btns, text="Borrar")
        self.btn_delete.pack(side="left", fill="x", expand=True)

    def _refresh_variable_list(self):
        """Redibuja toda la lista de variables"""
        # 1. Limpiar lista actual
        for w in self.vars_scroll_frame.winfo_children():
            w.destroy()
            
        if not self.current_event: return

        # 2. Dibujar filas
        for i, var in enumerate(self.current_event.variables):
            self._draw_variable_row(i, var)
            
    def _draw_variable_row(self, index, var):
        """Dibuja una fila individual"""
        # Color de fondo según selección
        bg_color = "#cce8ff" if index == self.selected_index else "white"
        
        row_frame = tk.Frame(self.vars_scroll_frame, bg=bg_color, pady=3, padx=3)
        row_frame.pack(fill="x", expand=True)
        
        # --- Eventos de Click (Selección) ---
        def on_click(e):
            self.selected_index = index
            self._refresh_variable_list()
        
        row_frame.bind("<Button-1>", on_click)
        
        # Etiqueta Nombre y Tipo
        lbl_text = f"{var.name}  [{type(var).__name__}]"
        lbl = tk.Label(row_frame, text=lbl_text, bg=bg_color, anchor="w", font=("Arial", 10))
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        lbl.bind("<Button-1>", on_click)
        
        # Evento Doble Click (Edición)
        if self.on_var_double_click:
            row_frame.bind("<Double-Button-1>", lambda e: self.on_var_double_click())
            lbl.bind("<Double-Button-1>", lambda e: self.on_var_double_click())

        # --- Botones Reordenar ---
        # Botón Bajar
        state_down = "disabled" if index == len(self.current_event.variables) - 1 else "normal"
        btn_down = ttk.Button(row_frame, text="▼", width=3, state=state_down,
                              command=lambda: self._move_variable(index, 1))
        btn_down.pack(side="right", padx=2)
        
        # Botón Subir
        state_up = "disabled" if index == 0 else "normal"
        btn_up = ttk.Button(row_frame, text="▲", width=3, state=state_up,
                            command=lambda: self._move_variable(index, -1))
        btn_up.pack(side="right", padx=2)

    def _move_variable(self, index, direction):
        """Mueve una variable arriba (-1) o abajo (+1)"""
        vars_list = self.current_event.variables
        new_index = index + direction
        
        if 0 <= new_index < len(vars_list):
            # Intercambiar
            vars_list[index], vars_list[new_index] = vars_list[new_index], vars_list[index]
            
            # Mover la selección con el elemento
            if self.selected_index == index:
                self.selected_index = new_index
            elif self.selected_index == new_index:
                self.selected_index = index
            
            self._refresh_variable_list()

    def _update_dynamic_options(self, event=None):
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.dynamic_widgets = {}
        self.var_options.dynamic_widgets = self.dynamic_widgets
        self.var_options.show_options(self.combo_type.get())

    def load_event(self, event_config):
        self.current_event = event_config
        self.selected_index = None # Resetear selección al cambiar evento
        
        if event_config is None:
            self.header_frame.pack_forget()
            self.content_frame.pack_forget()
            self._clear_header()
            self._refresh_variable_list() # Limpia la lista
            return

        self.header_frame.pack(fill="x", pady=(0, 10))
        self.content_frame.pack(fill="both", expand=True)
        
        self.entry_evt_name.config(state="normal")
        self.entry_evt_freq.config(state="normal")
        
        self.entry_evt_name.delete(0, tk.END)
        self.entry_evt_name.insert(0, event_config.name)
        self.entry_evt_freq.delete(0, tk.END)
        self.entry_evt_freq.insert(0, str(event_config.frequency))
        
        self._refresh_variable_list()

    def _save_header_changes(self, event=None):
        if not self.current_event: return
        self.current_event.name = self.entry_evt_name.get()
        try:
            self.current_event.frequency = int(self.entry_evt_freq.get())
        except:
            pass
        if self.on_event_update:
            self.on_event_update()

    def _clear_header(self):
        self.entry_evt_name.config(state="normal")
        self.entry_evt_name.delete(0, tk.END)
        self.entry_evt_freq.config(state="normal")
        self.entry_evt_freq.delete(0, tk.END)