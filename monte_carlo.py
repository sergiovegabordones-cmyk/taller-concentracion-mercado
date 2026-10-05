import matplotlib.pyplot as plt
import numpy as np

# Importar funciones de validación e indicadores desde indicadores.py
from indicadores import (
    calcular_cr_k,
    calcular_id,
    calcular_ie,
    calcular_ihh,
    validar_y_normalizar_cuotas,
)


def generar_cuotas_dirichlet(
    n_empresas: int, alpha: float = 1.0
) -> np.ndarray:
    """Genera un vector aleatorio de cuotas para N empresas que suma exactamente 1.0

    utilizando la distribución de Dirichlet.

    Parametros:
        n_empresas: Número de firmas en el mercado (N).
        alpha: Parámetro de concentración.
               - alpha = 1.0: Muestreo uniforme sobre el símplex de cuotas.
               - alpha < 1.0: Mercados más concentrados (monopolios/oligopolios).
               - alpha > 1.0: Mercados más homogéneos y simétricos.
    """
    if not (2 <= n_empresas <= 100):
        raise ValueError("El número de empresas (N) debe estar entre 2 y 100.")

    alpha_vector = np.full(n_empresas, alpha)
    cuotas = np.random.dirichlet(alpha_vector)
    return cuotas


def ejecutar_monte_carlo(
    n_empresas: int,
    n_iteraciones: int = 10000,
    indicador: str = "ihh",
    k_cr: int = 4,
    alpha: float = 1.0,
    escala_ihh_10k: bool = True,
    seed: int | None = None,
) -> np.ndarray:
    """Ejecuta una simulación de Monte Carlo para obtener la distribución empírica

    de un indicador de concentración de mercado seleccionado.

    Parametros:
        n_empresas (int): Número N de empresas (entre 2 y 100).
        n_iteraciones (int): Número de simulaciones a realizar.
        indicador (str): Indicador objetivo: 'cr_k', 'ihh', 'id', 'ie'.
        k_cr (int): Parámetro k para el CR_k (solo si indicador='cr_k').
        alpha (float): Parámetro de la distribución Dirichlet.
        escala_ihh_10k (bool): Si es True y indicador='ihh', retorna escala [0, 10,000].
        seed (int, optional): Semilla para reproducibilidad.

    Retorna:
        np.ndarray: Vector de tamaño (n_iteraciones,) con los valores simulados del indicador.
    """
    if seed is not None:
        np.random.seed(seed)

    indicadores_validos = ["cr_k", "ihh", "id", "ie"]
    indicador = indicador.lower()
    if indicador not in indicadores_validos:
        raise ValueError(
            f"Indicador no válido. Seleccione uno de: {indicadores_validos}"
        )

    resultados = np.zeros(n_iteraciones)

    for i in range(n_iteraciones):
        # 1. Generar cuotas aleatorias
        cuotas = generar_cuotas_dirichlet(n_empresas, alpha=alpha)

        # 2. Validar que la suma sea exactamente 1.0
        cuotas = validar_y_normalizar_cuotas(cuotas)

        # 3. Calcular el indicador seleccionado
        if indicador == "cr_k":
            resultados[i] = calcular_cr_k(cuotas, k=k_cr)
        elif indicador == "ihh":
            resultados[i] = calcular_ihh(cuotas, escala_10k=escala_ihh_10k)
        elif indicador == "id":
            resultados[i] = calcular_id(cuotas)
        elif indicador == "ie":
            resultados[i] = calcular_ie(cuotas)

    return resultados


# ==========================================
# Ejemplo de uso e integración
# ==========================================
if __name__ == "__main__":
    N_EMPRESAS = 10
    ITERACIONES = 50000
    INDICADOR_SELECCIONADO = "ihh"  # 'cr_k', 'ihh', 'id', 'ie'

    print(
        f"Ejecutando Monte Carlo ({ITERACIONES} iteraciones, N={N_EMPRESAS} empresas)..."
    )

    distribucion = ejecutar_monte_carlo(
        n_empresas=N_EMPRESAS,
        n_iteraciones=ITERACIONES,
        indicador=INDICADOR_SELECCIONADO,
        alpha=1.0,  # Distribución uniforme
        escala_ihh_10k=True,
        seed=42,
    )

    # Mostrar estadísticos descriptivos de la distribución generada
    print(f"\nResultados para {INDICADOR_SELECCIONADO.upper()}:")
    print(f"Media:                {np.mean(distribucion):.4f}")
    print(f"Desviación Estándar:  {np.std(distribucion):.4f}")
    print(f"Mínimo:               {np.min(distribucion):.4f}")
    print(f"Percentil 25 (Q1):    {np.percentile(distribucion, 25):.4f}")
    print(f"Mediana (Q2):         {np.median(distribucion):.4f}")
    print(f"Percentil 75 (Q3):    {np.percentile(distribucion, 75):.4f}")
    print(f"Máximo:               {np.max(distribucion):.4f}")