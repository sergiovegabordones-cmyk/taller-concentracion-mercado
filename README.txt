========================================================================
SISTEMA DE ANÁLISIS Y SIMULACIÓN DE CONCENTRACIÓN DE MERCADO

Este proyecto incluye un conjunto de módulos en Python y una interfaz
interactiva desarrollada en Streamlit para calcular indicadores de
concentración de mercado (CR_k, IHH, ID, IE) y ejecutar simulaciones de
Monte Carlo con la distribución de Dirichlet.

ESTRUCTURA DEL PROYECTO

.
├── indicadores.py       # Módulo con fórmulas teóricas y validación de cuotas
├── monte_carlo.py       # Algoritmo de simulación con distribución Dirichlet
├── app.py               # Aplicación principal e interfaz web en Streamlit
├── requirements.txt     # Dependencias necesarias para el despliegue
└── README.txt           # Instrucciones de configuración y ejecución local

REQUISITOS PREVIOS

Python 3.9 o superior instalado en el sistema.

Gestor de paquetes pip actualizado.

INSTRUCCIONES DE EJECUCIÓN EN LOCAL

Paso 1: Clonar o descargar el repositorio
Asegúrate de que todos los archivos (indicadores.py, monte_carlo.py,
app.py, requirements.txt) estén en la misma carpeta de trabajo.

Paso 2: Crear y activar un entorno virtual (Recomendado)

En Linux / macOS:
python3 -m venv venv
source venv/bin/activate

En Windows (PowerShell / Command Prompt):
python -m venv venv
.\venv\Scripts\activate

Paso 3: Instalar las dependencias
Ejecuta el siguiente comando para instalar las librerías necesarias:
pip install -r requirements.txt

Paso 4: Iniciar la aplicación en Streamlit
Ejecuta el comando para arrancar el servidor local:
streamlit run app.py

Paso 5: Abrir en el navegador
Streamlit abrirá automáticamente la aplicación en tu navegador predeterminado.
Si no se abre, accede manualmente a la dirección:
http://localhost:8501

DESPLIEGUE EN STREAMLIT COMMUNITY CLOUD

Sube este proyecto a un repositorio público en GitHub.

Ingresa a https://share.streamlit.io/ e inicia sesión con tu cuenta de GitHub.

Haz clic en "New app" e indica:

Repository: Tu repositorio de GitHub

Branch: main

Main file path: app.py

Haz clic en "Deploy!" para desplegar la app en la nube.
========================================================================