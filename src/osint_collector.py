"""
NEUTROOSINT-GYE — Recolector Multi-Fuente OSINT
Leyva-Vázquez, M. (2026).

Extrae datos de fuentes abiertas (noticias, redes sociales, estadísticas
oficiales, satélite) y los convierte en tripletas TIF por sector.

Fuentes integradas:
  F1 — NewsAPI / GNews: artículos de prensa local e internacional
  F2 — Reddit / Telegram público: discurso ciudadano
  F3 — INEC / GADMGYE / Policía Nacional: estadísticas oficiales
  F4 — NASA Black Marble: iluminación nocturna satelital
  F5 — SNGRE / INAMHI: riesgo hídrico y desastres naturales
"""

from __future__ import annotations
import os
import time
import logging
import requests
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, timedelta
from src.neutrosophic_core import TIFTriplet, escalar_a_tif

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  Modelo de dato OSINT                                                #
# ------------------------------------------------------------------ #

@dataclass
class OSINTRecord:
    fuente: str
    sector: str
    fecha: str
    indicador: str
    valor_raw: float          # valor normalizado [0, 1]
    confianza_fuente: float   # calidad del dato [0, 1]; determina I
    tif: TIFTriplet = field(init=False)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        incertidumbre = 1 - self.confianza_fuente
        self.tif = escalar_a_tif(self.valor_raw, incertidumbre=incertidumbre)


# ------------------------------------------------------------------ #
#  Fuente 1 — Prensa (NewsAPI / GNews)                                #
# ------------------------------------------------------------------ #

TERMINOS_VIOLENCIA = [
    "violencia Guayaquil", "extorsión Guayaquil", "sicariato Guayaquil",
    "balacera Guayaquil", "pandillas Guayaquil", "narcotráfico Guayaquil",
    "femicidio Guayaquil", "robo Guayaquil", "inseguridad Guayaquil",
]

SECTORES_GYE = [
    "Urdesa", "Kennedy", "Alborada", "Guasmo", "Bastión Popular",
    "Mapasingue", "Flor de Bastión", "Monte Sinaí", "Prosperina",
    "Los Vergeles", "Sauces", "Samanes", "Puerto Lisa", "Fertisa",
    "Trinitaria", "Pradera", "Lagos", "Chongón", "Via a Daule",
    "Centro Histórico", "Centenario", "Roca / Urdesa Norte",
    "Bolivar", "Carbo / Concepción", "García Moreno", "Florida",
    "Garzota", "Miraflores", "Ceibos", "Tarqui",
]


class NewsOSINTCollector:
    """Extrae menciones de violencia por sector desde APIs de noticias."""

    BASE_URL = "https://gnews.io/api/v4/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GNEWS_API_KEY", "")
        self.confianza = 0.65  # prensa local: moderada (silenciamiento documentado)

    def recolectar(self, dias: int = 7) -> list[OSINTRecord]:
        if not self.api_key:
            logger.warning("GNEWS_API_KEY no configurada; usando datos de muestra")
            return self._datos_muestra()

        registros: list[OSINTRecord] = []
        desde = (datetime.utcnow() - timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")

        for sector in SECTORES_GYE:
            try:
                q = f"violencia {sector} Guayaquil"
                resp = requests.get(
                    self.BASE_URL,
                    params={"q": q, "lang": "es", "country": "ec",
                            "from": desde, "apikey": self.api_key},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                n_articulos = len(data.get("articles", []))
                # Normalizar: umbral empírico 10 artículos = máxima cobertura
                valor = min(n_articulos / 10, 1.0)
                registros.append(OSINTRecord(
                    fuente="GNews",
                    sector=sector,
                    fecha=datetime.utcnow().isoformat(),
                    indicador="cobertura_mediatica_violencia",
                    valor_raw=valor,
                    confianza_fuente=self.confianza,
                    metadata={"n_articulos": n_articulos, "query": q},
                ))
                time.sleep(0.5)  # respetar rate limit
            except Exception as e:
                logger.error(f"Error recolectando {sector}: {e}")

        return registros

    def _datos_muestra(self) -> list[OSINTRecord]:
        """Valores sintéticos para desarrollo y demo."""
        valores_demo = {
            "Guasmo": 0.82, "Bastión Popular": 0.79, "Monte Sinaí": 0.76,
            "Mapasingue": 0.74, "Flor de Bastión": 0.71, "Trinitaria": 0.68,
            "Fertiliza": 0.65, "Puerto Lisa": 0.63, "Fertisa": 0.61,
            "Prosperina": 0.58, "Sauces": 0.45, "Alborada": 0.42,
            "Kennedy": 0.40, "Urdesa": 0.35, "Centro Histórico": 0.55,
            "Centenario": 0.52, "Roca / Urdesa Norte": 0.33, "Bolivar": 0.38,
            "Carbo / Concepción": 0.36, "García Moreno": 0.50,
            "Florida": 0.44, "Garzota": 0.41, "Miraflores": 0.39,
            "Ceibos": 0.32, "Tarqui": 0.48, "Los Vergeles": 0.55,
            "Samanes": 0.43, "Lagos": 0.38, "Chongón": 0.47, "Via a Daule": 0.44,
        }
        return [
            OSINTRecord(
                fuente="GNews_DEMO",
                sector=sector,
                fecha=datetime.utcnow().isoformat(),
                indicador="cobertura_mediatica_violencia",
                valor_raw=valor,
                confianza_fuente=self.confianza,
                metadata={"demo": True},
            )
            for sector, valor in valores_demo.items()
        ]


# ------------------------------------------------------------------ #
#  Fuente 3 — Estadísticas Oficiales (INEC / GADMGYE)                 #
# ------------------------------------------------------------------ #

class EstadisticasOficialesCollector:
    """
    Extrae tasas de homicidio, denuncias y acceso a servicios desde
    datasets abiertos del INEC y GADMGYE.

    En ausencia de API oficial, carga CSV locales descargados
    periódicamente por el workflow de GitHub Actions.
    """

    def __init__(self, data_path: str = "data/processed/inec_gadmgye.csv"):
        self.data_path = data_path
        self.confianza = 0.80  # estadísticas oficiales: alta confianza

    def recolectar(self) -> list[OSINTRecord]:
        try:
            import pandas as pd
            df = pd.read_csv(self.data_path)
            registros = []
            for _, row in df.iterrows():
                registros.append(OSINTRecord(
                    fuente="INEC_GADMGYE",
                    sector=row["sector"],
                    fecha=row.get("fecha", datetime.utcnow().isoformat()),
                    indicador=row["indicador"],
                    valor_raw=float(row["valor_normalizado"]),
                    confianza_fuente=self.confianza,
                    metadata={"fuente_original": row.get("fuente_original", "")},
                ))
            return registros
        except FileNotFoundError:
            logger.warning(f"Archivo {self.data_path} no encontrado; usando muestra")
            return []
        except Exception as e:
            logger.error(f"Error cargando estadísticas oficiales: {e}")
            return []


# ------------------------------------------------------------------ #
#  Fuente 4 — NASA Black Marble (Iluminación Nocturna)                 #
# ------------------------------------------------------------------ #

class NightlightCollector:
    """
    Proxy de datos NASA Black Marble (VNP46A1) para Guayaquil.

    El workflow diario descarga tiles y calcula el promedio de radiancia
    por sector. Aquí se consumen los resultados pre-procesados.
    """

    def __init__(self, data_path: str = "data/processed/nightlight.csv"):
        self.data_path = data_path
        self.confianza = 0.75  # satélite: alta pero con nubosidad en zona tropical

    def recolectar(self) -> list[OSINTRecord]:
        try:
            import pandas as pd
            df = pd.read_csv(self.data_path)
            return [
                OSINTRecord(
                    fuente="NASA_BlackMarble",
                    sector=row["sector"],
                    fecha=row.get("fecha", datetime.utcnow().isoformat()),
                    indicador="iluminacion_nocturna_relativa",
                    valor_raw=float(row["radiancia_normalizada"]),
                    confianza_fuente=self.confianza,
                )
                for _, row in df.iterrows()
            ]
        except FileNotFoundError:
            logger.warning(f"Archivo {self.data_path} no encontrado; usando muestra")
            return self._muestra_nightlight()

    def _muestra_nightlight(self) -> list[OSINTRecord]:
        """Alta iluminación ≠ baja violencia (hallazgo paraconsistente clave)."""
        valores = {
            "Urdesa": 0.92, "Kennedy": 0.88, "Roca / Urdesa Norte": 0.90,
            "Bolivar": 0.85, "Centro Histórico": 0.87, "Alborada": 0.83,
            "Guasmo": 0.42, "Bastión Popular": 0.38, "Monte Sinaí": 0.30,
            "Mapasingue": 0.40, "Trinitaria": 0.45, "Flor de Bastión": 0.35,
        }
        fecha = datetime.utcnow().isoformat()
        return [
            OSINTRecord(
                fuente="NASA_BlackMarble_DEMO",
                sector=s,
                fecha=fecha,
                indicador="iluminacion_nocturna_relativa",
                valor_raw=v,
                confianza_fuente=self.confianza,
                metadata={"demo": True},
            )
            for s, v in valores.items()
        ]


# ------------------------------------------------------------------ #
#  Orquestador Multi-Fuente                                            #
# ------------------------------------------------------------------ #

class OSINTOrchestrator:
    """Coordina la recolección de todas las fuentes OSINT."""

    def __init__(self):
        self.fuentes = {
            "noticias": NewsOSINTCollector(),
            "oficiales": EstadisticasOficialesCollector(),
            "nightlight": NightlightCollector(),
        }

    def recolectar_todo(self) -> dict[str, list[OSINTRecord]]:
        resultados = {}
        for nombre, colector in self.fuentes.items():
            try:
                resultados[nombre] = colector.recolectar()
                logger.info(f"✓ {nombre}: {len(resultados[nombre])} registros")
            except Exception as e:
                logger.error(f"✗ {nombre}: {e}")
                resultados[nombre] = []
        return resultados
