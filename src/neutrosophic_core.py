"""
NEUTROOSINT-GYE — Núcleo de Lógica Neutrosófica
Leyva-Vázquez, M. (2026). UBE / Universidad de Guayaquil.

Implementa la tripleta SVN (T, I, F) conforme a Smarandache (1998) y los
operadores de agregación SVNWA usados en todas las capas de la plataforma.

Camino B: diagnóstico estructural comunitario — sin predicción policial.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence
import math


@dataclass(frozen=True)
class TIFTriplet:
    """Valor de Verdad Neutrosófico: (Verdad, Indeterminación, Falsedad)."""
    T: float  # grado de verdad      [0, 1]
    I: float  # grado de indeterminación [0, 1]
    F: float  # grado de falsedad    [0, 1]

    def __post_init__(self) -> None:
        for name, v in [("T", self.T), ("I", self.I), ("F", self.F)]:
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{name}={v} fuera del rango [0,1]")
        if self.T + self.I + self.F > 1.0 + 1e-9:
            raise ValueError(
                f"T+I+F={self.T+self.I+self.F:.3f} > 1; tripleta no válida"
            )

    # ------------------------------------------------------------------ #
    #  Operadores de comparación (orden parcial neutrosófico)              #
    # ------------------------------------------------------------------ #

    def score(self) -> float:
        """Función de puntuación s = (2 + T - I - F) / 3 ∈ [0, 1]."""
        return (2 + self.T - self.I - self.F) / 3

    def accuracy(self) -> float:
        """Función de exactitud a = (T - F) ∈ [-1, 1]."""
        return self.T - self.F

    # ------------------------------------------------------------------ #
    #  Operaciones algebraicas                                             #
    # ------------------------------------------------------------------ #

    def union(self, other: "TIFTriplet") -> "TIFTriplet":
        """Unión neutrosófica: max(T), max(I), min(F)."""
        return TIFTriplet(
            T=max(self.T, other.T),
            I=max(self.I, other.I),
            F=min(self.F, other.F),
        )

    def intersection(self, other: "TIFTriplet") -> "TIFTriplet":
        """Intersección neutrosófica: min(T), min(I), max(F)."""
        return TIFTriplet(
            T=min(self.T, other.T),
            I=min(self.I, other.I),
            F=max(self.F, other.F),
        )

    def complement(self) -> "TIFTriplet":
        """Complemento: (F, 1-I, T)."""
        return TIFTriplet(T=self.F, I=1 - self.I, F=self.T)

    def __add__(self, other: "TIFTriplet") -> "TIFTriplet":
        """Suma algebraica neutrosófica (operador Λ)."""
        t = self.T + other.T - self.T * other.T
        i = self.I * other.I
        f = self.F * other.F
        total = t + i + f
        if total > 1.0:
            t, i, f = t / total, i / total, f / total
        return TIFTriplet(T=round(t, 6), I=round(i, 6), F=round(f, 6))

    def __repr__(self) -> str:
        return f"TIF(T={self.T:.3f}, I={self.I:.3f}, F={self.F:.3f})"


# ------------------------------------------------------------------ #
#  Agregación SVNWA                                                    #
# ------------------------------------------------------------------ #

def svnwa(triplets: Sequence[TIFTriplet], weights: Sequence[float] | None = None) -> TIFTriplet:
    """
    Single-Valued Neutrosophic Weighted Average (SVNWA).

    Si weights es None se usa media aritmética simple.
    Smarandache (1999), Ye (2014).
    """
    n = len(triplets)
    if n == 0:
        raise ValueError("Se necesita al menos una tripleta")
    if weights is None:
        weights = [1.0 / n] * n
    w = list(weights)
    if abs(sum(w) - 1.0) > 1e-6:
        s = sum(w)
        w = [wi / s for wi in w]

    T = 1 - math.prod((1 - t.T) ** wi for t, wi in zip(triplets, w))
    I = math.prod(t.I ** wi for t, wi in zip(triplets, w))
    F = math.prod(t.F ** wi for t, wi in zip(triplets, w))

    total = T + I + F
    if total > 1.0:
        T, I, F = T / total, I / total, F / total
    return TIFTriplet(T=round(T, 6), I=round(I, 6), F=round(F, 6))


# ------------------------------------------------------------------ #
#  Clasificación de regímenes de vulnerabilidad                        #
# ------------------------------------------------------------------ #

REGIMENES = {
    "crítico":     (0.80, 1.01),
    "alto":        (0.60, 0.80),
    "moderado":    (0.40, 0.60),
    "bajo":        (0.20, 0.40),
    "mínimo":      (0.00, 0.20),
}


def clasificar_regimen(tif: TIFTriplet) -> str:
    s = tif.score()
    for nombre, (lo, hi) in REGIMENES.items():
        if lo <= s < hi:
            return nombre
    return "mínimo"


# ------------------------------------------------------------------ #
#  Distancia neutrosófica (Hamming normalizada)                        #
# ------------------------------------------------------------------ #

def distancia_hamming(a: TIFTriplet, b: TIFTriplet) -> float:
    """Distancia de Hamming normalizada entre dos tripletas."""
    return (abs(a.T - b.T) + abs(a.I - b.I) + abs(a.F - b.F)) / 3


# ------------------------------------------------------------------ #
#  Escalado de valor crudo a tripleta neutrosófica                    #
# ------------------------------------------------------------------ #

def escalar_a_tif(valor: float, min_v: float = 0.0, max_v: float = 1.0,
                   incertidumbre: float = 0.15) -> TIFTriplet:
    """
    Convierte un indicador escalar normalizado en tripleta TIF.

    valor ↑  →  T ↑ (más verdad de riesgo),  F ↓
    incertidumbre representa la calidad del dato fuente (0 = perfecto).
    """
    v = (valor - min_v) / (max_v - min_v + 1e-9)
    v = max(0.0, min(1.0, v))
    T = v * (1 - incertidumbre)
    F = (1 - v) * (1 - incertidumbre)
    I = 1 - T - F
    I = max(0.0, I)
    total = T + I + F
    return TIFTriplet(
        T=round(T / total, 6),
        I=round(I / total, 6),
        F=round(F / total, 6),
    )
