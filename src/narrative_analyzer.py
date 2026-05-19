"""
NEUTROOSINT-GYE — Analizador Narrativo LLM + N-fsQCA
Leyva-Vázquez, M., Batista Hernández, N., Smarandache, F. (2026).

Implementa el pipeline Inter-Narrativo publicado en:
  "LLM + Neutrosophic fsQCA: Inter-Narrative Causal Consistency..."
  WorldS4 2026, Springer LNNS (Submission #304).

Detecta el silenciamiento de drivers estructurales comparando el
discurso mediático (prensa) con el conocimiento estructural (encuesta).
"""

from __future__ import annotations
import os
import json
import logging
import requests
from dataclasses import dataclass
from typing import Any
from src.neutrosophic_core import TIFTriplet, svnwa

logger = logging.getLogger(__name__)

# Drivers estructurales identificados empíricamente (n=179 encuesta UG)
DRIVERS_ESTRUCTURALES = {
    "weapons_traffic":    {"label": "Tráfico de armas",     "struct_score": 0.800},
    "extorsion":          {"label": "Extorsión",            "struct_score": 0.710},
    "prison_link":        {"label": "Nexo carcelario",      "struct_score": 0.730},
    "drug_routes":        {"label": "Rutas de narcotráfico","struct_score": 0.780},
    "economic_pressure":  {"label": "Presión económica",    "struct_score": 0.562},
    "territorial_war":    {"label": "Guerra territorial",   "struct_score": 0.740},
    "family_violence":    {"label": "Violencia familiar",   "struct_score": 0.620},
    "impunity":           {"label": "Impunidad",            "struct_score": 0.680},
}

SILENCING_THRESHOLD = -0.20  # brecha significativa (paper empírico)

# Modelos disponibles via OpenRouter
MODELOS_LLM = {
    "gemini-flash":  "google/gemini-flash-1.5",
    "llama-3":       "meta-llama/llama-3.1-8b-instruct",
    "phi-4":         "microsoft/phi-4",
    "qwen-3":        "qwen/qwen3-8b",
}


@dataclass
class NarrativeScore:
    driver: str
    label: str
    score_prensa: float       # puntuación media LLMs para texto de prensa
    score_estructural: float  # baseline de encuesta
    gap: float                # brecha (negativa = silenciamiento)
    tif: TIFTriplet           # representación neutrosófica del gap
    silenciado: bool


class NarrativeAnalyzer:
    """
    Analiza artículos de prensa usando múltiples LLMs y cuantifica
    el silenciamiento de drivers estructurales de violencia.
    """

    def __init__(self, api_key: str | None = None,
                 modelos: list[str] | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.modelos = modelos or list(MODELOS_LLM.keys())
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    # ------------------------------------------------------------------ #
    #  Scoring de un artículo para un driver                              #
    # ------------------------------------------------------------------ #

    def _prompt_scoring(self, texto: str, driver: str, label: str) -> str:
        return f"""Eres un analista de discurso periodístico especializado en violencia urbana.

Artículo:
\"\"\"
{texto[:2000]}
\"\"\"

Califica en una escala 0.0-1.0 cuánto énfasis otorga este artículo al driver estructural
"{label}" ({driver}) como causa de la violencia.

0.0 = completamente ignorado / ausente
0.5 = mencionado superficialmente
1.0 = analizado en profundidad como causa central

Responde ÚNICAMENTE con un número decimal entre 0.0 y 1.0. Sin explicación."""

    def _llamar_llm(self, modelo_key: str, prompt: str) -> float | None:
        if not self.api_key:
            return None
        modelo_id = MODELOS_LLM[modelo_key]
        try:
            resp = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"},
                json={"model": modelo_id,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 10, "temperature": 0.0},
                timeout=30,
            )
            resp.raise_for_status()
            contenido = resp.json()["choices"][0]["message"]["content"].strip()
            return float(contenido)
        except Exception as e:
            logger.warning(f"Error con {modelo_id}: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  Análisis de un conjunto de artículos                               #
    # ------------------------------------------------------------------ #

    def analizar_corpus(self, articulos: list[str]) -> list[NarrativeScore]:
        """
        Analiza el corpus completo y devuelve NarrativeScore por driver.
        Formula I = Var(scores_LLMs) / 0.25  (Leyva-Vázquez et al. 2026)
        """
        resultados = []

        for driver, info in DRIVERS_ESTRUCTURALES.items():
            label = info["label"]
            score_struct = info["struct_score"]
            scores_articulos = []

            for art in articulos:
                scores_modelos = []
                for modelo in self.modelos:
                    prompt = self._prompt_scoring(art, driver, label)
                    score = self._llamar_llm(modelo, prompt)
                    if score is not None:
                        scores_modelos.append(score)

                if scores_modelos:
                    media = sum(scores_modelos) / len(scores_modelos)
                    varianza = sum((s - media) ** 2 for s in scores_modelos) / len(scores_modelos)
                    scores_articulos.append((media, varianza))

            if not scores_articulos:
                # sin API: usar datos empíricos del paper publicado
                scores_articulos = self._scores_demo(driver)

            score_prensa = sum(m for m, _ in scores_articulos) / len(scores_articulos)
            var_media = sum(v for _, v in scores_articulos) / len(scores_articulos)

            gap = score_prensa - score_struct

            # Mapeo neutrosófico del gap
            T = max(0.0, score_struct)   # verdad del driver en realidad
            I = min(1.0, var_media / 0.25)  # indeterminación = varianza inter-LLM
            F_raw = max(0.0, -gap)          # falsedad = magnitud del silenciamiento
            total = T + I + F_raw
            if total > 1.0:
                T, I, F_raw = T/total, I/total, F_raw/total

            tif = TIFTriplet(
                T=round(T, 4),
                I=round(I, 4),
                F=round(F_raw, 4),
            )

            resultados.append(NarrativeScore(
                driver=driver,
                label=label,
                score_prensa=round(score_prensa, 4),
                score_estructural=score_struct,
                gap=round(gap, 4),
                tif=tif,
                silenciado=gap < SILENCING_THRESHOLD,
            ))

        return sorted(resultados, key=lambda x: x.gap)

    def _scores_demo(self, driver: str) -> list[tuple[float, float]]:
        """Datos empíricos del paper publicado (WorldS4 2026)."""
        demo = {
            "weapons_traffic":    [(0.356, 0.031)],
            "extorsion":          [(0.365, 0.028)],
            "prison_link":        [(0.390, 0.035)],
            "drug_routes":        [(0.490, 0.042)],
            "economic_pressure":  [(0.348, 0.025)],
            "territorial_war":    [(0.620, 0.038)],
            "family_violence":    [(0.580, 0.030)],
            "impunity":           [(0.440, 0.033)],
        }
        return demo.get(driver, [(0.5, 0.03)])


# ------------------------------------------------------------------ #
#  Resumen de silenciamiento para el dashboard                         #
# ------------------------------------------------------------------ #

def resumen_silenciamiento(scores: list[NarrativeScore]) -> dict[str, Any]:
    silenciados = [s for s in scores if s.silenciado]
    return {
        "total_drivers": len(scores),
        "drivers_silenciados": len(silenciados),
        "tasa_silenciamiento": len(silenciados) / len(scores) if scores else 0,
        "brecha_maxima": min(s.gap for s in scores) if scores else 0,
        "drivers_silenciados_lista": [
            {"driver": s.driver, "label": s.label,
             "gap": s.gap, "tif": str(s.tif)}
            for s in silenciados
        ],
    }
