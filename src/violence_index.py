"""
NEUTROOSINT-GYE — Índice Pluriversal de Vulnerabilidad Estructural (IPVE)
Leyva-Vázquez, M. (2026).

Calcula el IPVE tríadico (T, I, F) para cada sector de Guayaquil
integrando las 5 capas OSINT mediante SVNWA ponderado.

El IPVE es un diagnóstico estructural, NO una predicción de criminalidad.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any
from src.neutrosophic_core import TIFTriplet, svnwa, clasificar_regimen
from src.osint_collector import OSINTRecord

logger = logging.getLogger(__name__)

# Pesos de las 5 capas (justificación en docs/architecture.md)
PESOS_CAPAS = {
    "noticias":        0.20,  # C1: cobertura mediática
    "oficiales":       0.30,  # C2: estadísticas institucionales
    "nightlight":      0.15,  # C3: acceso a servicios (proxy iluminación)
    "narrativa":       0.20,  # C4: N-fsQCA silenciamiento
    "encuesta":        0.15,  # C5: percepción comunitaria
}


@dataclass
class SectorIPVE:
    sector: str
    ipve: TIFTriplet
    regimen: str
    capas: dict[str, TIFTriplet] = field(default_factory=dict)
    paraconsistente: bool = False
    descripcion_paraconsistencia: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector": self.sector,
            "T": self.ipve.T,
            "I": self.ipve.I,
            "F": self.ipve.F,
            "score": round(self.ipve.score(), 4),
            "regimen": self.regimen,
            "paraconsistente": self.paraconsistente,
            "descripcion_paraconsistencia": self.descripcion_paraconsistencia,
            "capas": {k: str(v) for k, v in self.capas.items()},
        }


class IPVECalculator:
    """
    Calcula el IPVE para todos los sectores de Guayaquil integrando
    los registros OSINT multi-fuente mediante SVNWA.
    """

    PARACONSISTENCIA_UMBRAL = 0.25  # diferencia T entre capas para detectar conflicto

    def __init__(self, pesos: dict[str, float] | None = None):
        self.pesos = pesos or PESOS_CAPAS

    def calcular(self, registros_por_fuente: dict[str, list[OSINTRecord]]) -> list[SectorIPVE]:
        """
        Entrada: dict {nombre_fuente: [OSINTRecord, ...]}
        Salida: lista de SectorIPVE ordenada por score descendente.
        """
        # Agrupar por sector
        por_sector: dict[str, dict[str, list[TIFTriplet]]] = {}
        for fuente, registros in registros_por_fuente.items():
            for rec in registros:
                por_sector.setdefault(rec.sector, {}).setdefault(fuente, []).append(rec.tif)

        resultados = []
        for sector, capas in por_sector.items():
            tif_capas: dict[str, TIFTriplet] = {}
            tripletas_ponderadas: list[TIFTriplet] = []
            pesos_usados: list[float] = []

            for capa_nombre, peso in self.pesos.items():
                if capa_nombre in capas and capas[capa_nombre]:
                    tif_capa = svnwa(capas[capa_nombre])
                    tif_capas[capa_nombre] = tif_capa
                    tripletas_ponderadas.append(tif_capa)
                    pesos_usados.append(peso)

            if not tripletas_ponderadas:
                logger.warning(f"Sector '{sector}' sin datos; omitido")
                continue

            # Normalizar pesos al subconjunto disponible
            suma_pesos = sum(pesos_usados)
            pesos_norm = [p / suma_pesos for p in pesos_usados]

            ipve = svnwa(tripletas_ponderadas, pesos_norm)
            regimen = clasificar_regimen(ipve)

            # Detección de paraconsistencia
            para, desc = self._detectar_paraconsistencia(tif_capas, sector)

            resultados.append(SectorIPVE(
                sector=sector,
                ipve=ipve,
                regimen=regimen,
                capas=tif_capas,
                paraconsistente=para,
                descripcion_paraconsistencia=desc,
                metadata={"n_capas": len(tripletas_ponderadas)},
            ))

        return sorted(resultados, key=lambda x: x.ipve.score(), reverse=True)

    def _detectar_paraconsistencia(self, capas: dict[str, TIFTriplet],
                                    sector: str) -> tuple[bool, str]:
        """
        Detecta conflicto entre capas: alta iluminación (nightlight bajo F)
        pero alta violencia de género (oficiales T alto) → paraconsistencia.
        Hallazgo clave documentado para Urdesa/Centro Histórico.
        """
        if "nightlight" not in capas or "oficiales" not in capas:
            return False, ""

        luz = capas["nightlight"]
        viol = capas["oficiales"]

        # Alta iluminación (luz.T alta = bien iluminado) + alta vulnerabilidad estructural
        if luz.T > 0.70 and viol.T > 0.55:
            return True, (
                f"{sector}: iluminación alta (luz.T={luz.T:.2f}) coexiste con "
                f"alta vulnerabilidad estructural (viol.T={viol.T:.2f}). "
                "El espacio bien iluminado NO es necesariamente seguro para mujeres. "
                "Un índice escalar ocultaría esta contradicción."
            )

        return False, ""


# ------------------------------------------------------------------ #
#  Generador de informe de diagnóstico                                 #
# ------------------------------------------------------------------ #

def generar_informe_diagnostico(sectores: list[SectorIPVE]) -> dict[str, Any]:
    """Produce el informe de diagnóstico estructural para el dashboard."""
    criticos = [s for s in sectores if s.regimen in ("crítico", "alto")]
    paraconsistentes = [s for s in sectores if s.paraconsistente]

    return {
        "total_sectores": len(sectores),
        "sectores_criticos": len(criticos),
        "sectores_paraconsistentes": len(paraconsistentes),
        "ipve_promedio": {
            "T": round(sum(s.ipve.T for s in sectores) / len(sectores), 4) if sectores else 0,
            "I": round(sum(s.ipve.I for s in sectores) / len(sectores), 4) if sectores else 0,
            "F": round(sum(s.ipve.F for s in sectores) / len(sectores), 4) if sectores else 0,
        },
        "top_5_vulnerables": [
            {"sector": s.sector, "regimen": s.regimen, "score": round(s.ipve.score(), 4)}
            for s in sectores[:5]
        ],
        "casos_paraconsistentes": [
            {"sector": s.sector, "descripcion": s.descripcion_paraconsistencia}
            for s in paraconsistentes
        ],
        "nota_etica": (
            "Este índice mide vulnerabilidad estructural acumulada. "
            "NO predice eventos criminales futuros ni debe usarse para "
            "justificar intervenciones policiales focalizadas."
        ),
    }
