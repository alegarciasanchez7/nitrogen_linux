"""
Gestor de configuración (Guardar/Cargar JSON) con memoria de archivo
"""
import json
import tkinter as tk
from tkinter import filedialog, messagebox

class ConfigManager:
    def __init__(self, conn_config_panel, events_list_panel):
        self.conn_config = conn_config_panel
        self.events_list = events_list_panel
        self.current_file_path = None  # Memoria del archivo actual

    def save_configuration(self):
        """
        Guarda la configuración. 
        - Si ya hay un archivo cargado, lo sobreescribe.
        - Si no, pide al usuario dónde guardar (Guardar Como).
        """
        if self.current_file_path:
            # Sobreescribir archivo existente
            self._save_to_file(self.current_file_path)
            messagebox.showinfo("Guardado", f"Configuración actualizada en:\n{self.current_file_path}")
        else:
            # Comportamiento 'Guardar Como'
            self._save_configuration_as()

    def _save_configuration_as(self):
        """Pide una ruta y guarda el archivo"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos", "*.*")],
            title="Guardar Configuración"
        )
        if filepath:
            self.current_file_path = filepath
            self._save_to_file(filepath)
            messagebox.showinfo("Guardado", "Configuración guardada correctamente.")

    def _save_to_file(self, filepath):
        """Lógica interna de guardado"""
        try:
            data = {
                "connection": self.conn_config.get_config(),
                "events": self.events_list.get_config()
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def load_configuration(self):
        """Carga una configuración y recuerda la ruta del archivo"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos", "*.*")],
            title="Cargar Configuración"
        )
        
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Restaurar Conexión
            if "connection" in data:
                self.conn_config.set_config(data["connection"])
            
            # 2. Restaurar Eventos
            if "events" in data:
                self.events_list.set_config(data["events"])
            
            # Si todo sale bien, recordamos este archivo
            self.current_file_path = filepath
            messagebox.showinfo("Cargado", f"Configuración cargada desde:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo de configuración:\n{e}")