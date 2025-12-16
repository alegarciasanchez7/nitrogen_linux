"""
Panel para gestionar la lista de diferentes eventos/mensajes
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.event_config import EventConfig

class EventsListPanel:
    def __init__(self, parent, on_event_selected_callback):
        self.parent = parent
        self.on_event_selected = on_event_selected_callback
        self.events = []
        self.selected_index = None

        # Frame Principal
        self.frame = ttk.LabelFrame(parent, text="2. Lista de Eventos", padding=10)
        
        # --- 1. BOTONES (Empaquetar PRIMERO con side=bottom para fijarlos abajo) ---
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(side="bottom", fill="x", pady=(5, 0)) # Padding arriba para separar de la lista

        ttk.Button(btn_frame, text="+ Nuevo Evento", command=self._add_event).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btn_frame, text="- Borrar", command=self._delete_event).pack(side="left", fill="x", expand=True, padx=2)

        # --- 2. LISTA (Empaquetar DESPUÉS para que ocupe el resto del espacio) ---
        self.listbox = tk.Listbox(self.frame, height=15, selectmode=tk.SINGLE, bg="#ffffff")
        self.listbox.pack(side="top", fill="both", expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def _add_event(self):
        # Crear evento por defecto
        new_evt = EventConfig(name=f"Evento_{len(self.events)+1}", frequency=1000)
        self.events.append(new_evt)
        self._refresh_list()
        
        # Seleccionar el nuevo evento automáticamente
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.listbox.event_generate("<<ListboxSelect>>")

    def _delete_event(self):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        del self.events[idx]
        self.selected_index = None
        self._refresh_list()
        # Disparar callback con None para limpiar el diseñador
        self.on_event_selected(None)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for evt in self.events:
            self.listbox.insert(tk.END, str(evt))

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        
        index = sel[0]
        self.selected_index = index
        selected_event = self.events[index]
        
        # Notificar al diseñador para cargar este evento
        self.on_event_selected(selected_event)

    def update_current_event_display(self):
        """Refresca el nombre/frecuencia en la lista si se cambia en el diseñador"""
        if self.selected_index is not None and self.selected_index < len(self.events):
            self.listbox.delete(self.selected_index)
            self.listbox.insert(self.selected_index, str(self.events[self.selected_index]))
            self.listbox.selection_set(self.selected_index)
    
    def get_config(self):
        """Retorna la configuración de eventos para guardar"""
        return [evt.to_dict() for evt in self.events]
    
    def set_config(self, events_data):
        """Carga la configuración de eventos desde un diccionario"""
        self.events = [EventConfig.from_dict(evt_dict) for evt_dict in events_data]
        self._refresh_list()
        # Seleccionar el primer evento si existe
        if self.events:
            self.listbox.selection_set(0)
            self.listbox.event_generate("<<ListboxSelect>>")