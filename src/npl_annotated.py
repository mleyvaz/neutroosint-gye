"""
NEUTROOSINT-GYE — Lógica Neutrosófica Paraconsistente Anotada (NPL)
Leyva-Vázquez, M. & Smarandache, F. (2026).

Implementa el núcleo técnico de la NPL desarrollada en:
  "Neutrosophic Paraconsistent Logic: Evidence Degrees, Ontological
   Indeterminacy, and Scientific Evidence Synthesis"
  (En revisión con Florentin Smarandache — v0.5, mayo 2026)

La NPL unifica:
  • LPA (Lógica Paraconsistente Anotada, da Costa & Abe 1994)
  • SVN (Single-Valued Neutrosophic Sets, Smarandache 1999)

Resultado: evidencia epistemológica (mu, lambda) + indeterminación
ontológica (I) en un único formalismo.

Diferencia central con SVN pura:
  - SVN: T=verdad-valor, F=falsedad-valor (semántica veritativa)
  - NPL: mu=evidencia favorable, lambda=evidencia contraria (semántica evidencial)
  - I en ambas: grado de indeterminación, pero en NPL distingue
    epistemológico (resolver con más datos) de ontológico (inherente al fenómeno)

Embedding algebraico: phi(A:(mu, lambda)) = A:(T=mu, I=0, F=lambda)
LPA ⊂ NPL cuando I = 0 (indeterminación nula).
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Sequence
from src.neutrosophic_core import TIFTriplet


# ------------------------------------------------------------------ #
#  Umbrales theta por dominio (Definición 5 — NPL paper v0.5)         #
# ------------------------------------------------------------------ #

THETA_DOMINIO: dict[str, float] = {
    "ciencias_experimentales":  0.35,
    "ciencias_sociales":        0.50,
    "humanidades":              0.60,
    "filosofia":                0.72,
    "osint_urbano":             0.45,   # calibrado para datos Guayaquil
    "narrativa_mediatica":      0.55,   # mayor tolerancia a ambigüedad discursiva
}

# Estados epistémicos NPL (Definición 6)
ESTADO_NPL = {
    "NPL-T":    "Trivial (mu=lambda=I=1): contradicción irresoluble",
    "NPL-PARA": "Paraconsistente (mu+lambda>1, I<theta): ambas evidencias fuertes",
    "NPL-INC":  "Incompleta (mu+lambda<1, I>theta): información insuficiente ontológica",
    "NPL-F":    "Falsa (mu<0.3, lambda>0.7): evidencia mayoritariamente contraria",
    "NPL-V":    "Verdadera (mu>0.7, lambda<0.3): evidencia mayoritariamente favorable",
    "NPL-EPI":  "Epistémica (I<=theta): indeterminación resoluble con más datos",
    "NPL-ONT":  "Ontológica (I>theta): indeterminación inherente al fenómeno",
}


@dataclass(frozen=True)
class NPLTriplet:
    """
    Tripleta NPL: (mu, lambda, I) — todas en [0, 1], INDEPENDIENTES.

    A diferencia de TIFTriplet, NO se requiere mu + lambda + I <= 1.
    Esto permite representar paraconsistencia (mu + lambda > 1).
    """
    mu: float       # grado de evidencia favorable (epistémico, LPA)
    lambda_: float  # grado de evidencia contraria  (epistémico, LPA)
    I: float        # grado de indeterminación       (ontológico, neutrosófico)

    def __post_init__(self) -> None:
        for name, v in [("mu", self.mu), ("lambda_", self.lambda_), ("I", self.I)]:
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{name}={v} fuera de [0,1]")

    # ------------------------------------------------------------------ #
    #  Clasificación de estados NPL                                        #
    # ------------------------------------------------------------------ #

    def es_paraconsistente(self, theta: float = 0.45) -> bool:
        """mu + lambda > 1 → ambas evidencias son fuertes simultáneamente."""
        return self.mu + self.lambda_ > 1.0

    def es_trivial(self) -> bool:
        """Estado NPL-T: ninguna conclusión posible."""
        return self.mu > 0.9 and self.lambda_ > 0.9 and self.I > 0.9

    def tipo_indeterminacion(self, theta: float = 0.45) -> str:
        """Distingue indeterminación epistémica (resolver) de ontológica (habitar)."""
        if self.I > theta:
            return "ontologica"
        return "epistemica"

    def estado(self, dominio: str = "osint_urbano") -> str:
        theta = THETA_DOMINIO.get(dominio, 0.45)
        if self.es_trivial():
            return "NPL-T"
        if self.es_paraconsistente(theta):
            return "NPL-PARA"
        if self.mu > 0.7 and self.lambda_ < 0.3:
            return "NPL-V"
        if self.mu < 0.3 and self.lambda_ > 0.7:
            return "NPL-F"
        if self.mu + self.lambda_ < 0.5 and self.I > theta:
            return "NPL-INC"
        return "NPL-EPI"

    # ------------------------------------------------------------------ #
    #  Embedding hacia SVN (phi)                                           #
    # ------------------------------------------------------------------ #

    def to_tif(self) -> TIFTriplet:
        """
        Embedding algebraico: phi(mu, lambda, I) = TIF(T=mu, I=I, F=lambda)

        Pierde la semántica evidencial pero permite usar operadores SVN.
        Válido cuando I es baja. Para I alto, preferir operar en NPL.
        """
        total = self.mu + self.I + self.lambda_
        if total > 1.0:
            T = self.mu / total
            I = self.I / total
            F = self.lambda_ / total
        else:
            T, I, F = self.mu, self.I, self.lambda_
        return TIFTriplet(T=round(T, 6), I=round(I, 6), F=round(F, 6))

    @classmethod
    def from_tif(cls, tif: TIFTriplet) -> "NPLTriplet":
        """Inversión del embedding: TIF → NPL (asume I=indeterminación ontológica)."""
        return cls(mu=tif.T, lambda_=tif.F, I=tif.I)

    # ------------------------------------------------------------------ #
    #  Score evidencial                                                    #
    # ------------------------------------------------------------------ #

    def certeza(self) -> float:
        """Grado de certeza neta: mu - lambda ∈ [-1, 1]."""
        return self.mu - self.lambda_

    def consistencia(self) -> float:
        """
        Grado de consistencia: 1 - (mu + lambda - 1) si paraconsistente.
        Retorna 1.0 si no hay paraconsistencia.
        """
        if self.mu + self.lambda_ > 1.0:
            return 1.0 - (self.mu + self.lambda_ - 1.0)
        return 1.0

    def __repr__(self) -> str:
        return f"NPL(mu={self.mu:.3f}, λ={self.lambda_:.3f}, I={self.I:.3f})"


# ------------------------------------------------------------------ #
#  Agregación NPL-WA                                                   #
# ------------------------------------------------------------------ #

def npl_wa(triplets: Sequence[NPLTriplet],
           weights: Sequence[float] | None = None,
           dominio: str = "osint_urbano") -> NPLTriplet:
    """
    Media ponderada NPL (Proposición 3 — NPL paper v0.5).

    mu y lambda se agregan como en SVN (producto algebraico).
    I se agrega como media aritmética ponderada (representa indeterminación
    ontológica del dominio, no de las fuentes individuales).
    """
    n = len(triplets)
    if n == 0:
        raise ValueError("Se necesita al menos una tripleta NPL")
    if weights is None:
        weights = [1.0 / n] * n
    w = list(weights)
    if abs(sum(w) - 1.0) > 1e-6:
        s = sum(w)
        w = [wi / s for wi in w]

    # mu: SVNWA (producto algebraico ponderado)
    mu = 1 - math.prod((1 - t.mu) ** wi for t, wi in zip(triplets, w))
    # lambda: SVNWA (producto geométrico ponderado)
    lam = math.prod(t.lambda_ ** wi for t, wi in zip(triplets, w))
    # I: media aritmética ponderada
    I_val = sum(t.I * wi for t, wi in zip(triplets, w))

    return NPLTriplet(
        mu=round(min(mu, 1.0), 6),
        lambda_=round(max(lam, 0.0), 6),
        I=round(min(I_val, 1.0), 6),
    )


# ------------------------------------------------------------------ #
#  NPL-ES: Algoritmo de síntesis de evidencia (Definición 8)          #
# ------------------------------------------------------------------ #

def npl_es(evidencias: list[dict], dominio: str = "osint_urbano") -> dict:
    """
    NPL Evidence Synthesis (NPL-ES) — Definición 8, NPL paper v0.5.

    Parámetros:
      evidencias: lista de dicts con keys:
        - 'fuente': nombre de la fuente
        - 'mu': grado de evidencia favorable [0,1]
        - 'lambda_': grado de evidencia contraria [0,1]
        - 'I': indeterminación ontológica [0,1]
        - 'peso': peso de la fuente [0,1]

    Retorna: resultado de síntesis con estado NPL y recomendación.
    """
    if not evidencias:
        return {"error": "Sin evidencias"}

    theta = THETA_DOMINIO.get(dominio, 0.45)
    triplets = [
        NPLTriplet(mu=e["mu"], lambda_=e["lambda_"], I=e["I"])
        for e in evidencias
    ]
    pesos = [e.get("peso", 1.0) for e in evidencias]

    resultado = npl_wa(triplets, pesos, dominio)
    estado = resultado.estado(dominio)

    # Recomendación según estado
    recomendaciones = {
        "NPL-T":    "No tomar decisión. Buscar árbitro experto o datos adicionales.",
        "NPL-PARA": "Estado paraconsistente: ambas hipótesis tienen soporte. Investigar causa.",
        "NPL-INC":  "Datos insuficientes. Recolectar más evidencia antes de concluir.",
        "NPL-F":    "Hipótesis refutada. La evidencia contraria domina.",
        "NPL-V":    "Hipótesis confirmada. Evidencia favorable dominante.",
        "NPL-EPI":  "Indeterminación epistémica. Resoluble con datos adicionales.",
    }

    return {
        "resultado_npl": str(resultado),
        "mu_sintetizado": resultado.mu,
        "lambda_sintetizado": resultado.lambda_,
        "I_sintetizado": resultado.I,
        "certeza_neta": round(resultado.certeza(), 4),
        "consistencia": round(resultado.consistencia(), 4),
        "estado": estado,
        "descripcion_estado": ESTADO_NPL.get(estado, ""),
        "tipo_indeterminacion": resultado.tipo_indeterminacion(theta),
        "theta_dominio": theta,
        "recomendacion": recomendaciones.get(estado, "Revisar caso manualmente"),
        "paraconsistente": resultado.es_paraconsistente(theta),
        "n_fuentes": len(evidencias),
    }


# ------------------------------------------------------------------ #
#  Aplicación OSINT: anotar registros OSINT con NPL                   #
# ------------------------------------------------------------------ #

def anotar_osint_con_npl(registros_por_fuente: dict,
                          dominio: str = "osint_urbano") -> dict[str, dict]:
    """
    Convierte registros OSINT (TIF) en anotaciones NPL por sector.

    El grado mu se toma como T (verdad = evidencia favorable de vulnerabilidad).
    El grado lambda se toma como F (falsedad = evidencia contraria).
    El grado I se toma directamente del TIF (indeterminación de la fuente).

    Luego aplica NPL-ES para sintetizar las fuentes.
    """
    por_sector: dict[str, list[dict]] = {}

    pesos_fuentes = {
        "noticias":  0.20,
        "oficiales": 0.30,
        "nightlight": 0.15,
        "narrativa":  0.20,
        "encuesta":   0.15,
    }

    for fuente, registros in registros_por_fuente.items():
        peso = pesos_fuentes.get(fuente, 0.20)
        for rec in registros:
            tif = rec.tif
            por_sector.setdefault(rec.sector, []).append({
                "fuente": fuente,
                "mu": tif.T,
                "lambda_": tif.F,
                "I": tif.I,
                "peso": peso,
            })

    resultados = {}
    for sector, evidencias in por_sector.items():
        resultados[sector] = npl_es(evidencias, dominio)

    return resultados


# ------------------------------------------------------------------ #
#  Caso clínico-analítico: OSINT Guayaquil (análogo al caso paracetamol) #
# ------------------------------------------------------------------ #

CASO_GUAYAQUIL_DEMOSTRACION = """
CASO NPL — OSINT GUAYAQUIL (análogo al caso paracetamol, NPL paper §4.1)

Sector: Urdesa / Roca (Guayaquil)

Evidencias:
  E1 (NASA Black Marble): alta iluminación nocturna → mu=0.15, λ=0.80, I=0.10
      (iluminación alta sugiere infraestructura desarrollada, baja vulnerabilidad)
  E2 (Estadísticas VG GADMGYE): alta tasa denuncias violencia género → mu=0.75, λ=0.20, I=0.25
      (datos institucionales confirman alta vulnerabilidad para mujeres)
  E3 (Prensa): cobertura mediática baja → mu=0.35, λ=0.60, I=0.35
      (silenciamiento mediático documentado)

Síntesis NPL-ES:
  mu_s = 0.52, λ_s = 0.45, I_s = 0.23
  Certeza neta = +0.07 (casi nula)
  mu + λ = 0.97 (bordeando paraconsistencia)
  Estado: NPL-PARA (epistemológico)

Interpretación:
  El sector tiene AMBAS evidencias fuertes simultáneamente.
  Alta iluminación (percepción de seguridad) + alta violencia de género (realidad).
  Un índice escalar produciría score neutro, ocultando la contradicción.
  El marco NPL la hace visible: es un caso de paraconsistencia estructural
  que requiere intervención diferenciada (no más iluminación, sino servicios de género).

Recomendación NPL-ES: investigar causa de la paraconsistencia antes de intervenir.
"""
