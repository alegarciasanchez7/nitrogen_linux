# nITROGEN Linux Edition 🐧

Este proyecto es una implementación en **Python** de la herramienta de generación de datos sintéticos **nITROGEN**, diseñada originalmente para Windows.

El objetivo principal es permitir la ejecución de simulaciones de tráfico IoT en entornos **Linux** (desarrollado y testado en Fedora), manteniendo la lógica de generación de datos y la conectividad descrita en el manual original.

## 🚀 Funcionalidades

* **Generación de Variables:**
    * 🔢 **Numéricas:** Aleatorias, secuenciales o constantes.
    * 🔤 **Texto:** Cadenas aleatorias y tokens (longitud fija/variable).
    * 📅 **Fechas:** Timestamps actuales, fijos o incrementales.
    * 📋 **Listas:** Selección de valores predefinidos (aleatoria o secuencial).
* **Conectividad:**
    * 📡 **MQTT:** Conexión a brokers (ej. Mosquitto) para envío de datos en tiempo real.
* **Interfaz Gráfica (GUI):**
    * Interfaz amigable desarrollada con `tkinter` para configurar y lanzar simulaciones fácilmente.

## 🛠️ Requisitos e Instalación

Este proyecto requiere **Python 3.x**.

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/alegarciasanchez7/nitrogen_linux.git](https://github.com/alegarciasanchez7/nitrogen_linux.git)
    cd nitrogen_linux
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

    *Nota para usuarios de Fedora/Linux:* Si tienes problemas con la interfaz gráfica, asegúrate de tener instalado Tkinter:
    ```bash
    sudo dnf install python3-tkinter
    ```

## ▶️ Ejecución

Para iniciar la interfaz gráfica y configurar tu simulación:

```bash
python3 gui_app.py
```

## ✒️ Autor
**Alejandro García Sánchez** Escuela Superior de Ingeniería (Ing. Informática)