# nITROGEN Linux Edition 🐧

Este proyecto es una implementación en **Python** de la herramienta de generación de datos sintéticos **nITROGEN**, diseñada originalmente para Windows.

El objetivo principal es permitir la ejecución de simulaciones de tráfico IoT en entornos **Linux** (desarrollado y testado en Fedora), manteniendo la lógica de generación de datos y la conectividad descrita en el manual original.

## 🚀 Funcionalidades

* **Generación de Variables:**
    * 🔢 **Numéricas:** Aleatorias, secuenciales, constantes o con tendencia (lineal/exponencial).
    * 🔤 **Texto:** Cadenas aleatorias o generadas mediante expresiones regulares.
    * 📅 **Fechas:** Timestamps actuales, fijos o incrementales.
    * 📋 **Listas:** Selección de valores predefinidos (aleatoria o secuencial).
    * 📍 **Puntos:** Coordenadas 2D/3D con valores aleatorios o secuenciales por eje.
    * ✅ **Booleanas:** Valores true/false aleatorios o por probabilidad.
* **Conectividad:**
    * 📡 **MQTT:** Conexión a brokers (ej. Mosquitto) para envío de datos en tiempo real.
    * 🐰 **RabbitMQ (AMQP):** Soporte para colas de mensajes mediante protocolo AMQP.
    * 📄 **Archivo:** Exportación de datos a ficheros locales.
* **Gestión de Eventos:**
    * ⚡ **Múltiples Eventos:** Crea y gestiona diferentes eventos con variables y frecuencias independientes.
    * 🎯 **Configuración por Evento:** Cada evento puede tener su propia frecuencia de envío y conjunto de variables.
* **Persistencia de Configuración:**
    * 💾 **Guardar/Cargar:** Exporta e importa configuraciones completas en formato JSON.
    * 🔄 **Reutilización:** Guarda tus configuraciones de simulación para uso futuro.
* **Interfaz Gráfica (GUI):**
    * Interfaz modular desarrollada con `tkinter` para configurar y lanzar simulaciones fácilmente.
    * 📊 **Consola de Log:** Visualización en tiempo real del estado de la simulación.
    * 🎨 **Panel de Diseño:** Formularios dinámicos que se adaptan al tipo de variable seleccionada.

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