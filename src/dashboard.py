"""
NEUTROOSINT-GYE — Dashboard Streamlit
Leyva-Vázquez, M. (2026).

Interfaz web interactiva para la plataforma NEUTROOSINT-GYE.
Ejecutar: streamlit run src/dashboard.py --server.port 8503

7 páginas:
  1. Inicio & Contexto Ético
  2. Mapa IPVE por Sector
  3. Análisis Narrativo (Silenciamiento)
  4. Detector de Paraconsistencia
  5. Series Temporales OSINT
  6. Comparador de Capas
  7. Exportar Informe
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import json
from pathlib import Path

from src.neutrosophic_core import TIFTriplet
from src.osint_collector import OSINTOrchestrator
from src.narrative_analyzer import NarrativeAnalyzer, resumen_silenciamiento
from src.violence_index import IPVECalculator, generar_informe_diagnostico
from src.paraconsistency_detector import ParaconsistencyDetector
from src.ethical_safeguards import DISCLAIMER_CIENTIFICO, EthicalSafeguard

# ------------------------------------------------------------------ #
#  Configuración de página                                             #
# ------------------------------------------------------------------ #

st.set_page_config(
    page_title="NEUTROOSINT-GYE",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGINAS = [
    "🏠 Inicio & Marco Ético",
    "🗺️ Mapa IPVE por Sector",
    "📰 Análisis Narrativo",
    "⚡ Detector de Paraconsistencia",
    "📈 Series Temporales OSINT",
    "🔍 Comparador de Capas",
    "📄 Exportar Informe",
]


# ------------------------------------------------------------------ #
#  Caché de datos                                                      #
# ------------------------------------------------------------------ #

@st.cache_data(ttl=3600)
def cargar_datos():
    orquestador = OSINTOrchestrator()
    registros = orquestador.recolectar_todo()
    calculador = IPVECalculator()
    sectores = calculador.calcular(registros)
    return registros, sectores


@st.cache_data(ttl=7200)
def cargar_analisis_narrativo():
    analyzer = NarrativeAnalyzer()
    articulos_demo = [
        "Guayaquil registra aumento de homicidios en zonas periféricas.",
        "Autoridades refuerzan patrullaje en sectores de alta criminalidad.",
        "Extorsión a negocios en Guasmo sigue sin respuesta institucional.",
    ]
    return analyzer.analizar_corpus(articulos_demo)


# ------------------------------------------------------------------ #
#  Barra lateral                                                       #
# ------------------------------------------------------------------ #

def sidebar():
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/"
        "Universidad_de_Guayaquil_-_Logo.png/200px-Universidad_de_Guayaquil_-_Logo.png",
        width=120,
    )
    st.sidebar.title("NEUTROOSINT-GYE")
    st.sidebar.caption("Inteligencia de Fuentes Abiertas | Lógica Neutrosófica")
    st.sidebar.divider()
    pagina = st.sidebar.radio("Navegación", PAGINAS)
    st.sidebar.divider()
    st.sidebar.caption(
        "Camino B — Diagnóstico Estructural Comunitario\n"
        "NO es un sistema de predicción policial."
    )
    return pagina


# ------------------------------------------------------------------ #
#  Páginas                                                             #
# ------------------------------------------------------------------ #

def pagina_inicio():
    st.title("🔬 NEUTROOSINT-GYE")
    st.subheader("Plataforma de Inteligencia de Fuentes Abiertas basada en Lógica Neutrosófica")

    col1, col2, col3 = st.columns(3)
    col1.metric("Sectores monitoreados", "30")
    col2.metric("Fuentes OSINT integradas", "5")
    col3.metric("Drivers narrativos analizados", "8")

    st.divider()
    st.subheader("⚖️ Marco Ético — Camino B")
    st.warning(DISCLAIMER_CIENTIFICO)

    with st.expander("¿Qué es el IPVE?"):
        st.markdown("""
**Índice Pluriversal de Vulnerabilidad Estructural (IPVE)**

El IPVE es una tripleta neutrosófica (T, I, F) que captura:
- **T (Verdad)**: grado de vulnerabilidad estructural confirmada
- **I (Indeterminación)**: incertidumbre de los datos disponibles
- **F (Falsedad)**: grado en que la evidencia contradice la hipótesis de vulnerabilidad

A diferencia de un índice escalar, el IPVE **preserva las contradicciones** entre fuentes,
lo que permite detectar casos donde un barrio bien iluminado coexiste con alta violencia
de género (paraconsistencia estructural).

**Referencia:** Leyva-Vázquez et al. (2026). WorldS4, Springer LNNS.
""")

    with st.expander("Arquitectura de 5 capas"):
        st.markdown("""
| Capa | Fuente | Peso | Indicadores clave |
|------|--------|------|-------------------|
| C1 Narrativa mediática | GNews / NewsAPI | 20% | Cobertura por sector |
| C2 Estadísticas oficiales | INEC / GADMGYE | 30% | Homicidios, denuncias VG |
| C3 Iluminación satelital | NASA Black Marble | 15% | Radiancia nocturna |
| C4 N-fsQCA narrativo | LLM + OpenRouter | 20% | Silenciamiento de drivers |
| C5 Encuesta comunitaria | UG (n=151) | 15% | Percepción de riesgo |
""")


def pagina_mapa(sectores):
    st.title("🗺️ Mapa IPVE por Sector — Guayaquil")

    informe = generar_informe_diagnostico(sectores)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sectores analizados", informe["total_sectores"])
    col2.metric("Sectores críticos/altos", informe["sectores_criticos"],
                delta_color="inverse")
    col3.metric("Casos paraconsistentes", informe["sectores_paraconsistentes"])
    ipve_avg = informe["ipve_promedio"]
    col4.metric("IPVE promedio (T)", f"{ipve_avg['T']:.3f}")

    st.divider()
    df = pd.DataFrame([s.to_dict() for s in sectores])
    df = df.sort_values("score", ascending=False)

    col_tabla, col_detalle = st.columns([2, 1])

    with col_tabla:
        st.subheader("Tabla de sectores ordenada por vulnerabilidad")
        st.dataframe(
            df[["sector", "T", "I", "F", "score", "regimen", "paraconsistente"]],
            use_container_width=True,
            hide_index=True,
        )

    with col_detalle:
        st.subheader("Top 5 más vulnerables")
        for item in informe["top_5_vulnerables"]:
            color = "🔴" if item["regimen"] == "crítico" else "🟠"
            st.markdown(
                f"{color} **{item['sector']}** — {item['regimen']} "
                f"(score={item['score']:.3f})"
            )
        st.caption(informe["nota_etica"])


def pagina_narrativo():
    st.title("📰 Análisis Narrativo — Silenciamiento de Drivers Estructurales")
    st.markdown(
        "Basado en: *LLM + N-fsQCA: Inter-Narrative Causal Consistency*, "
        "WorldS4 2026 (Submission #304)."
    )

    with st.spinner("Ejecutando pipeline N-fsQCA..."):
        scores = cargar_analisis_narrativo()
        resumen = resumen_silenciamiento(scores)

    col1, col2, col3 = st.columns(3)
    col1.metric("Drivers analizados", resumen["total_drivers"])
    col2.metric("Drivers silenciados", resumen["drivers_silenciados"])
    col3.metric("Tasa de silenciamiento",
                f"{resumen['tasa_silenciamiento']:.0%}")

    st.divider()
    df_scores = pd.DataFrame([
        {
            "Driver": s.label,
            "Prensa (T_media)": s.score_prensa,
            "Estructura (encuesta)": s.score_estructural,
            "Brecha (gap)": s.gap,
            "T_neutro": s.tif.T,
            "I_neutro": s.tif.I,
            "Silenciado": "✓" if s.silenciado else "",
        }
        for s in scores
    ])
    st.dataframe(df_scores, use_container_width=True, hide_index=True)

    st.subheader("Drivers con mayor silenciamiento (brecha < -0.20)")
    for item in resumen["drivers_silenciados_lista"]:
        st.error(
            f"**{item['label']}** — gap={item['gap']:.3f} | TIF: {item['tif']}"
        )


def pagina_paraconsistencia(sectores, registros):
    st.title("⚡ Detector de Paraconsistencia Inter-Fuente")
    st.markdown(
        "Detecta contradicciones estructurales entre fuentes OSINT. "
        "Las contradicciones son información, no errores."
    )

    capas_por_sector: dict = {}
    for s in sectores:
        capas_por_sector[s.sector] = s.capas

    detector = ParaconsistencyDetector()
    conflictos = detector.detectar(capas_por_sector)
    resumen = detector.resumen(conflictos)

    col1, col2, col3 = st.columns(3)
    col1.metric("Conflictos detectados", resumen["total_conflictos"])
    col2.metric("Contradicciones críticas",
                resumen["por_tipo"].get("contradiccion", 0))
    col3.metric("Sectores afectados", len(resumen["sectores_afectados"]))

    st.divider()
    if resumen["conflictos_criticos"]:
        st.subheader("⚠️ Casos de Paraconsistencia Estructural")
        for caso in resumen["conflictos_criticos"]:
            with st.expander(
                f"{caso['sector']} — {caso['fuentes']} (d={caso['distancia']:.3f})"
            ):
                st.markdown(caso["interpretacion"])
    else:
        st.success("No se detectaron contradicciones críticas en los datos actuales.")

    st.info(resumen["mensaje_metodologico"])


def pagina_exportar(sectores):
    st.title("📄 Exportar Informe de Diagnóstico")

    informe = generar_informe_diagnostico(sectores)
    safeguard = EthicalSafeguard()

    st.subheader("Configurar exportación")
    usuario = st.text_input("Usuario / Institución", placeholder="Universidad de Guayaquil")
    proposito = st.selectbox("Propósito del uso", [
        "community_structural_diagnosis",
        "academic_research",
        "journalism_investigation",
        "public_health_planning",
        "urban_planning",
        "civil_society_monitoring",
    ])
    nivel = st.selectbox("Granularidad", ["sector", "zona", "ciudad"])

    if st.button("Generar informe"):
        if not usuario:
            st.error("Ingrese el nombre de usuario/institución.")
            return
        try:
            resultado_auditoria = safeguard.auditar(
                usuario=usuario, accion="exportar_informe",
                proposito=proposito, nivel=nivel,
            )
            st.success(f"Informe aprobado — {resultado_auditoria['timestamp']}")
            for adv in resultado_auditoria.get("advertencias", []):
                st.warning(adv)
            st.json(informe)
            json_str = json.dumps(informe, ensure_ascii=False, indent=2)
            st.download_button(
                "Descargar JSON",
                data=json_str,
                file_name="neutroosint_gye_informe.json",
                mime="application/json",
            )
        except PermissionError as e:
            st.error(str(e))


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #

def main():
    pagina = sidebar()
    registros, sectores = cargar_datos()

    if pagina == PAGINAS[0]:
        pagina_inicio()
    elif pagina == PAGINAS[1]:
        pagina_mapa(sectores)
    elif pagina == PAGINAS[2]:
        pagina_narrativo()
    elif pagina == PAGINAS[3]:
        pagina_paraconsistencia(sectores, registros)
    elif pagina == PAGINAS[4]:
        st.title("📈 Series Temporales OSINT")
        st.info("Módulo en desarrollo. Disponible en v1.1 (Q3 2026).")
    elif pagina == PAGINAS[5]:
        st.title("🔍 Comparador de Capas")
        st.info("Módulo en desarrollo. Disponible en v1.1 (Q3 2026).")
    elif pagina == PAGINAS[6]:
        pagina_exportar(sectores)


if __name__ == "__main__":
    main()
