import json
import tkinter as tk
from tkinter import filedialog, messagebox
from core.event_config import EventConfig
# Importamos todas las variables para poder reconstruirlas
from variables_type import (
    NumericVariable, StringVariable, ListVariable, 
    DateVariable, PointVariable, BooleanVariable
)

class ConfigManager:
    def __init__(self, root, conn_panel, events_panel, designer_panel):
        self.root = root
        self.conn_panel = conn_panel
        self.events_panel = events_panel
        self.designer_panel = designer_panel

    def save_configuration(self):
        """Recopila todo el estado y lo guarda en JSON"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Nitrogen Config", "*.json"), ("Todos", "*.*")],
            title="Guardar Configuración de Simulación"
        )
        if not filepath:
            return

        try:
            # 1. Obtener Configuración de Conexión
            conn_data = self.conn_panel.get_config()
            # Convertimos los widgets de tkinter a sus valores de texto para guardar
            # El método get_config original devuelve los widgets en 'options', hay que extraer el valor
            clean_options = {}
            for key, widget in conn_data["options"].items():
                if isinstance(widget, tk.Entry):
                    clean_options[key] = widget.get()
            
            conn_save_data = {
                "type": conn_data["type"],
                "frequency": conn_data["frequency"],
                "options": clean_options
            }

            # 2. Obtener Eventos y Variables
            events_data = []
            for evt in self.events_panel.events:
                evt_dict = {
                    "name": evt.name,
                    "frequency": evt.frequency,
                    "enabled": evt.enabled,
                    "variables": []
                }
                
                for var in evt.variables:
                    # Guardamos el diccionario de atributos (__dict__) y añadimos el tipo de clase
                    var_data = var.__dict__.copy()
                    var_data["__type__"] = type(var).__name__
                    evt_dict["variables"].append(var_data)
                
                events_data.append(evt_dict)

            # 3. Estructura Final
            full_config = {
                "connection": conn_save_data,
                "events": events_data
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")

        except Exception as e:
            messagebox.showerror("Error Guardando", f"No se pudo guardar: {str(e)}")

    def load_configuration(self):
        """Carga un JSON y restaura el estado de la aplicación"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Nitrogen Config", "*.json"), ("Todos", "*.*")],
            title="Cargar Configuración"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. Restaurar Conexión
            if "connection" in data:
                self.conn_panel.set_config(data["connection"])

            # 2. Restaurar Eventos
            if "events" in data:
                self.events_panel.events.clear() # Limpiar lista actual
                
                for evt_data in data["events"]:
                    new_evt = EventConfig(evt_data["name"], evt_data["frequency"])
                    new_evt.enabled = evt_data.get("enabled", True)
                    
                    # Reconstruir variables
                    for var_data in evt_data["variables"]:
                        var_type = var_data.pop("__type__") # Extraer tipo y quitarlo de los datos
                        
                        # Instanciamos la clase correcta dinámicamente
                        var_class = globals()[var_type] 
                        
                        # Creamos una instancia 'vacía' o dummy y luego le inyectamos los datos
                        # Truco: Usamos __new__ para no obligarnos a pasar argumentos al __init__
                        var_obj = var_class.__new__(var_class)
                        var_obj.__dict__.update(var_data)
                        
                        new_evt.variables.append(var_obj)
                    
                    self.events_panel.events.append(new_evt)
                
                # Refrescar la GUI de la lista
                self.events_panel._refresh_list()
                # Limpiar el diseñador
                self.events_panel.on_event_selected(None)

            messagebox.showinfo("Éxito", "Configuración cargada correctamente.")

        except Exception as e:
            messagebox.showerror("Error Cargando", f"Archivo corrupto o incompatible: {str(e)}")
            print(e) # Para depuración en consola