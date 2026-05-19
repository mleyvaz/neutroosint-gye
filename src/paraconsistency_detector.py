"""
NEUTROOSINT-GYE — Detector de Paraconsistencia Inter-Fuente
Leyva-Vázquez, M. (2026).

Detecta y clasifica contradicciones estructurales entre fuentes OSINT.
Una contradicción no es un error: es información sobre la complejidad real.

Fundamentación: Lógica Paraconsistente (da Costa 1974) + SVN (Smarandache 1998).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any
from src.neutrosophic_core import TIFTriplet, distancia_hamming, svnwa

logger = logging.getLogger(__name__)


@dataclass
class Conflicto:
    sector: str
    fuente_a: str
    fuente_b: str
    tif_a: TIFTriplet
    tif_b: TIFTriplet
    distancia: float
    tipo: str           # "contradiccion" | "divergencia" | "incertidumbre"
    interpretacion: str
    severidad: str      # "alta" | "media" | "baja"


TIPOS_CONFLICTO = {
    "contradiccion": {
        "descripcion": "Las fuentes reportan estados opuestos sobre el mismo fenómeno",
        "umbral_distancia": 0.40,
        "severidad": "alta",
    },
    "divergencia": {
        "descripcion": "Las fuentes difieren significativamente sin contradecirse",
        "umbral_distancia": 0.25,
        "severidad": "media",
    },
    "incertidumbre": {
        "descripcion": "Una fuente tiene alta indeterminación mientras la otra es precisa",
        "umbral_i": 0.40,
        "severidad": "baja",
    },
}


class ParaconsistencyDetector:
    """
    Detecta conflictos entre capas OSINT usando distancia de Hamming
    neutrosófica y clasifica su tipo epistemológico.
    """

    UMBRAL_CONTRADICCION = 0.40
    UMBRAL_DIVERGENCIA = 0.25
    UMBRAL_I_ALTA = 0.40

    def detectar(self, capas_por_sector: dict[str, dict[str, TIFTriplet]]) -> list[Conflicto]:
        """
        Para cada sector analiza todos los pares de capas y detecta conflictos.
        """
        conflictos: list[Conflicto] = []

        for sector, capas in capas_por_sector.items():
            nombres = list(capas.keys())
            for i in range(len(nombres)):
                for j in range(i + 1, len(nombres)):
                    fuente_a, fuente_b = nombres[i], nombres[j]
                    tif_a = capas[fuente_a]
                    tif_b = capas[fuente_b]

                    conflicto = self._evaluar_par(
                        sector, fuente_a, fuente_b, tif_a, tif_b
                    )
                    if conflicto:
                        conflictos.append(conflicto)

        return sorted(conflictos, key=lambda c: c.distancia, reverse=True)

    def _evaluar_par(self, sector: str, fa: str, fb: str,
                     tif_a: TIFTriplet, tif_b: TIFTriplet) -> Conflicto | None:
        d = distancia_hamming(tif_a, tif_b)

        if d >= self.UMBRAL_CONTRADICCION:
            tipo = "contradiccion"
            interp = self._interpretar_contradiccion(sector, fa, fb, tif_a, tif_b)
            sev = "alta"
        elif d >= self.UMBRAL_DIVERGENCIA:
            tipo = "divergencia"
            interp = (
                f"{sector}: {fa} (T={tif_a.T:.2f}) y {fb} (T={tif_b.T:.2f}) "
                "divergen en la caracterización del riesgo estructural. "
                "Posibles causas: diferente población objetivo, lag temporal, "
                "o sesgo de registro."
            )
            sev = "media"
        elif max(tif_a.I, tif_b.I) >= self.UMBRAL_I_ALTA:
            tipo = "incertidumbre"
            fuente_incierta = fa if tif_a.I > tif_b.I else fb
            interp = (
                f"{sector}: {fuente_incierta} presenta alta indeterminación "
                f"(I={max(tif_a.I, tif_b.I):.2f}). Posiblemente datos incompletos "
                "o fuente con baja cobertura del sector."
            )
            sev = "baja"
        else:
            return None

        return Conflicto(
            sector=sector,
            fuente_a=fa,
            fuente_b=fb,
            tif_a=tif_a,
            tif_b=tif_b,
            distancia=round(d, 4),
            tipo=tipo,
            interpretacion=interp,
            severidad=sev,
        )

    def _interpretar_contradiccion(self, sector: str, fa: str, fb: str,
                                    tif_a: TIFTriplet, tif_b: TIFTriplet) -> str:
        # Caso emblemático: alta iluminación + alta violencia de género
        if (fa == "nightlight" or fb == "nightlight"):
            otro = fb if fa == "nightlight" else fa
            luz = tif_a if fa == "nightlight" else tif_b
            viol = tif_b if fa == "nightlight" else tif_a
            if luz.T > 0.70 and viol.T > 0.55:
                return (
                    f"⚠ PARACONSISTENCIA ESTRUCTURAL en {sector}: "
                    f"Alta iluminación nocturna (T_luz={luz.T:.2f}) coexiste con "
                    f"alta vulnerabilidad estructural reportada por {otro} "
                    f"(T_viol={viol.T:.2f}). "
                    "'Barrio bien iluminado' ≠ 'barrio seguro para todas las personas'. "
                    "Esto revela que la inversión en infraestructura física no correlaciona "
                    "necesariamente con reducción de violencia de género."
                )

        return (
            f"CONTRADICCIÓN en {sector}: {fa} (T={tif_a.T:.2f}, F={tif_a.F:.2f}) "
            f"contradice a {fb} (T={tif_b.T:.2f}, F={tif_b.F:.2f}). "
            f"Distancia Hamming={distancia_hamming(tif_a, tif_b):.3f}. "
            "Se recomienda triangulación con fuente adicional antes de tomar "
            "decisiones de política pública."
        )

    # ------------------------------------------------------------------ #
    #  Resumen ejecutivo para el dashboard                                 #
    # ------------------------------------------------------------------ #

    def resumen(self, conflictos: list[Conflicto]) -> dict[str, Any]:
        por_tipo = {"contradiccion": 0, "divergencia": 0, "incertidumbre": 0}
        for c in conflictos:
            por_tipo[c.tipo] = por_tipo.get(c.tipo, 0) + 1

        return {
            "total_conflictos": len(conflictos),
            "por_tipo": por_tipo,
            "sectores_afectados": list({c.sector for c in conflictos}),
            "conflictos_criticos": [
                {
                    "sector": c.sector,
                    "fuentes": f"{c.fuente_a} vs {c.fuente_b}",
                    "tipo": c.tipo,
                    "distancia": c.distancia,
                    "interpretacion": c.interpretacion,
                }
                for c in conflictos if c.severidad == "alta"
            ],
            "mensaje_metodologico": (
                "Los conflictos inter-fuente son información epistemológica valiosa. "
                "Un modelo escalar eliminaría estas contradicciones mediante promedio, "
                "destruyendo la señal. El marco neutrosófico las preserva y las hace visibles."
            ),
        }
