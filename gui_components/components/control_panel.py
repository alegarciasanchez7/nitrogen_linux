"""
Panel de control con botones y consola de logs
"""
import tkinter as tk
from tkinter import ttk


class ControlPanel:
    def __init__(self, parent):
        self.parent = parent
        
        # Frame principal
        self.frame = ttk.LabelFrame(parent, text="3. Control", padding=10)
        
        # Frame para botones (arriba)
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill="x", pady=(0, 5))
        
        self.btn_start = ttk.Button(
            buttons_frame, 
            text="▶ INICIAR SIMULACIÓN"
        )
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(
            buttons_frame, 
            text="⏹ DETENER", 
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(
            buttons_frame, 
            text="LIMPIAR",
            command=self.clear_console
        )
        self.btn_clear.pack(side="left", padx=5)
        
        # Consola de logs (abajo)
        self.log_area = tk.Text(self.frame, height=8, bg="#222", fg="#0f0")
        self.log_area.pack(fill="both", expand=True)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def log(self, msg):
        """Añade un mensaje al log"""
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def clear_console(self):
        """Limpia la consola de logs"""
        self.log_area.delete(1.0, tk.END)
