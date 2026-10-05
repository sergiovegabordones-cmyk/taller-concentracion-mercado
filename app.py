import time
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Importar funciones de los módulos locales
from indicadores import (
    calcular_cr_k,
    calcular_id,
    calcular_ie,
    calcular_ihh,
    validar_y_normalizar_cuotas,
)
from monte_carlo import ejecutar_monte_carlo, generar_cuotas_dirichlet

# Configuración inicial de la página Streamlit
st.set_page_config(
    page_title="Simulador de Concentración de Mercado",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES Y DE CÁLCULO
# ---------------------------------------------------------


def evaluar_carga_computacional(iteraciones: int, n_empresas: int):
    """Evalúa la carga estimada de la simulación y proyecta latencia."""
    ops_estimadas = iteraciones * n_empresas

    if ops_estimadas > 2_000_000:
        st.warning(
            f"⚠️ **Advertencia de Alta Carga Computacional**: "
            f"Has configurado {iteraciones:,} iteraciones para {n_empresas} empresas (~{ops_estimadas:,} operaciones). "
            f"La simulación puede tomar varios segundos y elevar el consumo de memoria/CPU."
        )
    elif ops_estimadas > 500_000:
        st.info(
            f"ℹ️ **Carga Moderada**: {iteraciones:,} iteraciones y {n_empresas} empresas (~{ops_estimadas:,} operaciones)."
        )


def calcular_caso_particular(
    cuotas: np.ndarray, indicador: str, k_cr: int = 4
) -> float:
    """Calcula el valor del indicador seleccionado para un caso particular de cuotas."""
    s = validar_y_normalizar_cuotas(cuotas)
    indicador = indicador.lower()

    if indicador == "cr_k":
        return calcular_cr_k(s, k=k_cr)
    elif indicador == "ihh":
        return calcular_ihh(s, escala_10k=True)
    elif indicador == "id":
        return calcular_id(s)
    elif indicador == "ie":
        return calcular_ie(s)
    else:
        raise ValueError("Indicador no reconocido.")


def obtener_clasificacion_teorica(
    valor: float, indicador: str
) -> tuple[str, str]:
    """Retorna la clasificación cualitativa estándar según literatura de Organización Industrial."""
    if indicador == "ihh":
        if valor < 1500:
            return (
                "Desconcentrado / Competitivo",
                "IHH < 1,500 (Baja concentración)",
            )
        elif 1500 <= valor <= 2500:
            return (
                "Moderadamente Concentrado",
                "1,500 ≤ IHH ≤ 2,500 (Concentración moderada)",
            )
        else:
            return (
                "Altamente Concentrado",
                "IHH > 2,500 (Alta concentración / Posible poder de mercado)",
            )
    elif indicador == "cr_k":
        if valor < 0.40:
            return "Baja Concentración", "CR_k < 40%"
        elif 0.40 <= valor <= 0.70:
            return "Concentración Moderada / Oligopolio Débil", "40% ≤ CR_k ≤ 70%"
        else:
            return "Alta Concentración / Oligopolio Estrecho", "CR_k > 70%"
    else:
        return (
            "N/A",
            "Clasificación no estandarizada para este índice específico",
        )


# ---------------------------------------------------------
# BARRA LATERAL (CONFIGURACIÓN)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de Simulación")

# 1. Selector de Indicador y N Empresas
indicador_sel = st.sidebar.selectbox(
    "Selecciona el Indicador de Concentración:",
    options=["ihh", "cr_k", "id", "ie"],
    format_func=lambda x: {
        "ihh": "Índice de Herfindahl-Hirschman (IHH)",
        "cr_k": "Ratio de Concentración (CR_k)",
        "id": "Índice de Dominancia (ID)",
        "ie": "Índice de Entropía (IE)",
    }[x],
)

k_cr_val = 4
if indicador_sel == "cr_k":
    k_cr_val = st.sidebar.slider(
        "Número de empresas Top (k):", min_value=1, max_value=10, value=4
    )

n_empresas_input = st.sidebar.slider(
    "Número de Empresas (N):", min_value=2, max_value=100, value=10
)

# 2. Entrada de Iteraciones (por defecto 1,000)
n_iteraciones_input = st.sidebar.number_input(
    "Número de Iteraciones de Monte Carlo:",
    min_value=100,
    max_value=100000,
    value=1000,
    step=500,
)

evaluar_carga_computacional(n_iteraciones_input, n_empresas_input)

st.sidebar.markdown("---")
st.sidebar.header("📌 Caso Particular de Análisis")

modo_ingreso = st.sidebar.radio(
    "Modo de ingreso del caso particular:",
    options=["Generación Aleatoria Puntual", "Entrada Manual de Cuotas"],
)

cuotas_caso = None

if modo_ingreso == "Generación Aleatoria Puntual":
    alpha_caso = st.sidebar.slider(
        "Parámetro Alpha (Dirichlet):",
        0.1,
        5.0,
        1.0,
        help="Valores < 1 generan mercados más concentrados.",
    )
    if st.sidebar.button("🎲 Generar Nuevo Caso"):
        st.session_state["cuotas_caso"] = generar_cuotas_dirichlet(
            n_empresas_input, alpha=alpha_caso
        )

    if "cuotas_caso" not in st.session_state or len(
        st.session_state["cuotas_caso"]
    ) != n_empresas_input:
        st.session_state["cuotas_caso"] = generar_cuotas_dirichlet(
            n_empresas_input, alpha=alpha_caso
        )

    cuotas_caso = st.session_state["cuotas_caso"]

else:  # Entrada Manual
    st.sidebar.caption(
        f"Ingresa {n_empresas_input} cuotas separadas por coma (en % o entre 0 y 1). Deberán sumar 100% o 1.0:"
    )
    ejemplo_str = ", ".join(
        [
            str(round(100 / n_empresas_input, 1))
            for _ in range(n_empresas_input)
        ]
    )
    input_manual = st.sidebar.text_area("Cuotas:", value=ejemplo_str, height=100)

    try:
        cuotas_parsed = [float(x.strip()) for x in input_manual.split(",")]
        if len(cuotas_parsed) != n_empresas_input:
            st.sidebar.error(
                f"Debes ingresar exactamente {n_empresas_input} cuotas (se ingresaron {len(cuotas_parsed)})."
            )
        else:
            cuotas_caso = validar_y_normalizar_cuotas(cuotas_parsed)
    except Exception as e:
        st.sidebar.error(f"Error en formato de cuotas: {e}")

# ---------------------------------------------------------
# PANEL PRINCIPAL Y EJECUCIÓN
# ---------------------------------------------------------
st.title("📊 Análisis de Concentración de Mercado: Monte Carlo & Caso Particular")

if st.button("🚀 Ejecutar Simulación de Monte Carlo", type="primary"):
    with st.spinner("Ejecutando iteraciones de Monte Carlo..."):
        start_time = time.time()

        # Ejecución de Monte Carlo
        distribucion_mc = ejecutar_monte_carlo(
            n_empresas=n_empresas_input,
            n_iteraciones=n_iteraciones_input,
            indicador=indicador_sel,
            k_cr=k_cr_val,
            alpha=1.0,
            escala_ihh_10k=True,
        )

        elapsed_time = time.time() - start_time
        st.session_state["distribucion_mc"] = distribucion_mc
        st.session_state["tiempo_mc"] = elapsed_time

# Verificar si existen resultados en sesión
if "distribucion_mc" in st.session_state and cuotas_caso is not None:
    distribucion = st.session_state["distribucion_mc"]
    tiempo = st.session_state["tiempo_mc"]

    # Cálculo del Caso Particular
    valor_caso = calcular_caso_particular(
        cuotas_caso, indicador_sel, k_cr=k_cr_val
    )
    percentil_caso = (
        np.sum(distribucion <= valor_caso) / len(distribucion)
    ) * 100

    # Guardar en sesión para módulo interactivo
    st.session_state["valor_caso"] = valor_caso
    st.session_state["percentil_caso"] = percentil_caso

    # Métricas clave arriba
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tiempo de Cómputo", f"{tiempo:.3f} s")
    col2.metric("Media de la Distribución", f"{np.mean(distribucion):.2f}")
    col3.metric("Valor Caso Particular", f"{valor_caso:.2f}")
    col4.metric("Percentil Cuantitativo", f"{percentil_caso:.1f}%")

    st.markdown("---")

    # ---------------------------------------------------------
    # 4. GRÁFICO PLOTLY (HISTOGRAMA / DENSIDAD + LÍNEA DESTACADA)
    # ---------------------------------------------------------
    st.subheader("📈 Distribución Empírica vs. Caso Particular")

    unidades_eje_x = {
        "ihh": "Puntos de IHH (Escala 0 a 10,000)",
        "cr_k": f"Proporción de Mercado Acumulada (CR_{k_cr_val})",
        "id": "Índice de Dominancia (Escala 0 a 1)",
        "ie": "Entropía (Nats / Unidades de Información)",
    }[indicador_sel]

    nombre_indicador = {
        "ihh": "Índice de Herfindahl-Hirschman (IHH)",
        "cr_k": f"Ratio de Concentración (CR_{k_cr_val})",
        "id": "Índice de Dominancia (ID)",
        "ie": "Índice de Entropía (IE)",
    }[indicador_sel]

    fig = go.Figure()

    # Histograma de Monte Carlo
    fig.add_trace(
        go.Histogram(
            x=distribucion,
            histnorm="probability density",
            name="Simulación Monte Carlo",
            marker_color="#1f77b4",
            opacity=0.65,
            nbinsx=50,
        )
    )

    # Línea Vertical Destacada para el Caso Particular
    fig.add_vline(
        x=valor_caso,
        line_width=3.5,
        line_dash="dash",
        line_color="#FF4B4B",
        annotation_text=f"Caso Particular: {valor_caso:.2f} (P{percentil_caso:.1f})",
        annotation_position="top right",
        annotation_font=dict(size=13, color="#FF4B4B"),
    )

    fig.update_layout(
        title=f"Distribución de Monte Carlo para {nombre_indicador} (N = {n_empresas_input} empresas)",
        xaxis_title=f"{nombre_indicador} [{unidades_eje_x}]",
        yaxis_title="Densidad de Probabilidad",
        template="plotly_white",
        height=500,
        bargap=0.05,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # MÓDULO EVALUADOR INTERACTIVO (CUESTIONARIO)
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("🧠 Módulo Evaluador Interactivo")
    st.write(
        "Con base en el indicador calculado y su posición en la distribución, evalúa el nivel de concentración de este caso particular:"
    )

    opciones_eval = [
        "Desconcentrado / Competitivo",
        "Moderadamente Concentrado",
        "Altamente Concentrado / Dominante",
    ]

    respuesta_usuario = st.radio(
        "¿Cómo clasificarías la estructura de mercado observada en el caso particular?",
        options=opciones_eval,
        key="eval_radio",
    )

    if st.button("Validar Diagnóstico"):
        clasif_teorica, criterio_texto = obtener_clasificacion_teorica(
            valor_caso, indicador_sel
        )

        st.markdown("#### 💬 Retroalimentación Cuantitativa Explicativa:")

        # Evaluación respecto a umbrales
        if indicador_sel in ["ihh", "cr_k"]:
            if (
                respuesta_usuario.split(" ")[0].lower()
                in clasif_teorica.lower()
            ):
                st.success(
                    f"¡Correcto! El mercado se clasifica como **{clasif_teorica}**."
                )
            else:
                st.error(
                    f"Diagnóstico Impreciso. La clasificación teórica correcta es **{clasif_teorica}**."
                )

            st.write(f"📌 **Criterio Técnico Estándar**: {criterio_texto}")
        else:
            st.info(
                f"Para el indicador **{indicador_sel.upper()}**, la evaluación se realiza principalmente en términos relativos."
            )

        # Contextualización basada en el Percentil de Monte Carlo
        st.write(
            f"📊 **Análisis Posicional (Percentil {percentil_caso:.1f}%)**:"
        )
        if percentil_caso > 75:
            st.write(
                f"El caso particular se ubica en el **{100 - percentil_caso:.1f}% superior** de concentración teórica "
                f"para un mercado de {n_empresas_input} empresas. Esto indica una estructura significativamente más asimétrica "
                f"y concentrada que el promedio aleatorio."
            )
        elif percentil_caso < 25:
            st.write(
                f"El caso particular presenta una concentración **inferior al 75%** de los mercados simétricos simulados. "
                f"Las cuotas de mercado se encuentran distribuidas de forma sustancialmente más homogénea que el promedio."
            )
        else:
            st.write(
                f"El caso particular se sitúa en la **zona media (intercuartil)** de la distribución de Monte Carlo, "
                f"siendo representativo de una estructura de mercado con asimetría moderada."
            )

else:
    st.info(
        "👈 Ajusta los parámetros en la barra lateral y haz clic en **'Ejecutar Simulación de Monte Carlo'** para comenzar."
    )