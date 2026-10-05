import numpy as np


def validar_y_normalizar_cuotas(cuotas: list | np.ndarray) -> np.ndarray:
    """Valida que las cuotas pertenezcan al rango válido [0, 100%] o [0, 1]

    y que la suma total equivalga al 100% (1.0).
    Retorna un array de NumPy con cuotas en el intervalo [0, 1].
    """
    s = np.array(cuotas, dtype=float)

    if np.any(s < 0):
        raise ValueError("Error: Existen cuotas con valores negativos.")

    # Si algún valor es superior a 1.0, asumimos que están expresadas en porcentaje [0, 100]
    if np.any(s > 1.0):
        if np.any(s > 100.0):
            raise ValueError(
                "Error: Existen cuotas individuales superiores al 100%."
            )
        s = s / 100.0

    # Validar que la suma sea equivalente a 1.0 (tolerancia para imprecisiones de flotante)
    suma_total = np.sum(s)
    if not np.isclose(suma_total, 1.0, atol=1e-5):
        raise ValueError(
            f"Error: La suma de las cuotas es {suma_total:.4f}, debe ser exactamente 1.0 (o 100%)."
        )

    return s


def calcular_cr_k(cuotas: np.ndarray, k: int = 4) -> float:
    """Calcula el Ratio de Concentración de las k mayores empresas (CR_k)."""
    if k <= 0:
        raise ValueError("El valor de 'k' debe ser mayor que 0.")
    cuotas_ordenadas = np.sort(cuotas)[::-1]
    return float(np.sum(cuotas_ordenadas[:k]))


def calcular_ihh(
    cuotas: np.ndarray, escala_10k: bool = False
) -> float:
    """Calcula el Índice de Herfindahl-Hirschman (IHH).

    Si escala_10k=True, multiplica el resultado por 10,000.
    """
    ihh = np.sum(cuotas**2)
    return float(ihh * 10000 if escala_10k else ihh)


def calcular_id(cuotas: np.ndarray) -> float:
    """Calcula el Índice de Dominancia (ID)."""
    ihh = np.sum(cuotas**2)
    if ihh == 0:
        return 0.0
    id_val = np.sum(cuotas**4) / (ihh**2)
    return float(id_val)


def calcular_ie(cuotas: np.ndarray) -> float:
    """Calcula el Índice de Entropía (IE)."""
    # Filtrar cuotas mayores a 0 para evitar logaritmo de cero (0 * log(0) = 0)
    s_positivas = cuotas[cuotas > 0]
    ie = -np.sum(s_positivas * np.log(s_positivas))
    return float(ie)


def calcular_indicadores_concentracion(
    cuotas: list | np.ndarray, k: int = 4
) -> dict:
    """Función integradora que valida datos y retorna todos los indicadores."""
    s = validar_y_normalizar_cuotas(cuotas)

    return {
        f"CR_{k}": calcular_cr_k(s, k=k),
        "IHH (Escala 0-1)": calcular_ihh(s, escala_10k=False),
        "IHH (Escala 0-10,000)": calcular_ihh(s, escala_10k=True),
        "Índice de Dominancia (ID)": calcular_id(s),
        "Índice de Entropía (IE)": calcular_ie(s),
    }


# ==========================================
# Ejemplo de uso
# ==========================================
if __name__ == "__main__":
    # Ejemplo 1: Cuotas expresadas en porcentajes (suman 100)
    cuotas_porcentaje = [40.0, 30.0, 15.0, 10.0, 5.0]

    print("--- Mercado A (Cuotas en %) ---")
    resultados_a = calcular_indicadores_concentracion(
        cuotas_porcentaje, k=3
    )
    for k, v in resultados_a.items():
        print(f"{k}: {v:.4f}")

    # Ejemplo 2: Cuotas expresadas en proporción [0, 1] (suman 1.0)
    cuotas_proporcion = [0.50, 0.25, 0.15, 0.10]

    print("\n--- Mercado B (Cuotas en [0, 1]) ---")
    resultados_b = calcular_indicadores_concentracion(
        cuotas_proporcion, k=2
    )
    for k, v in resultados_b.items():
        print(f"{k}: {v:.4f}")