"""
NEUTROOSINT-GYE — Marco Ético Camino B
Leyva-Vázquez, M. (2026).

Implementa las salvaguardas éticas para garantizar que la plataforma opere
como laboratorio comunitario de diagnóstico estructural, NO como herramienta
de vigilancia o predicción policial.

Referencia: Leyva-Vázquez (2026), "Camino B: Pluriversal Digital Twin".
"""

from __future__ import annotations
import json
import datetime
from pathlib import Path


PROPOSITOS_PROHIBIDOS = [
    "predictive_policing",
    "individual_surveillance",
    "insurance_pricing",
    "real_estate_speculation",
    "ethnic_profiling",
    "immigration_enforcement",
    "employer_screening",
    "credit_scoring",
]

GRANULARIDAD_MINIMA = "sector"  # nunca debajo de sector (manzana, dirección, individuo)

USOS_PERMITIDOS = [
    "community_structural_diagnosis",
    "policy_advocacy",
    "academic_research",
    "journalism_investigation",
    "public_health_planning",
    "urban_planning",
    "civil_society_monitoring",
]


class EthicalSafeguard:
    """Auditor ético integrado. Se ejecuta antes de cualquier exportación."""

    def __init__(self, log_path: str = "data/audit_log.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def validar_proposito(self, proposito: str) -> None:
        if proposito in PROPOSITOS_PROHIBIDOS:
            raise PermissionError(
                f"Propósito '{proposito}' explícitamente prohibido por el "
                "Marco Ético Camino B. La plataforma no puede usarse para "
                f"{proposito}. Ver docs/ethical_framework.md."
            )

    def validar_granularidad(self, nivel: str) -> None:
        jerarquia = ["sector", "zona", "ciudad", "provincia"]
        if nivel not in jerarquia:
            raise ValueError(
                f"Nivel de granularidad '{nivel}' no reconocido. "
                f"Niveles permitidos: {jerarquia}"
            )
        idx_minimo = jerarquia.index(GRANULARIDAD_MINIMA)
        idx_solicitado = jerarquia.index(nivel)
        if idx_solicitado < idx_minimo:
            raise PermissionError(
                f"La granularidad '{nivel}' está por debajo del mínimo "
                f"permitido ('{GRANULARIDAD_MINIMA}'). No se generan mapas "
                "de calor a nivel de manzana o individuo."
            )

    def registrar_acceso(self, usuario: str, accion: str, proposito: str,
                         nivel: str, sectores: list[str]) -> None:
        entrada = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "usuario": usuario,
            "accion": accion,
            "proposito_declarado": proposito,
            "granularidad": nivel,
            "sectores": sectores,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")

    def auditar(self, usuario: str, accion: str, proposito: str,
                nivel: str = "sector", sectores: list[str] | None = None) -> dict:
        """
        Punto de entrada único para todas las operaciones de exportación.
        Valida, registra y devuelve el resultado de la auditoría.
        """
        self.validar_proposito(proposito)
        self.validar_granularidad(nivel)
        self.registrar_acceso(
            usuario=usuario,
            accion=accion,
            proposito=proposito,
            nivel=nivel,
            sectores=sectores or [],
        )
        return {
            "aprobado": True,
            "advertencias": self._generar_advertencias(proposito, nivel),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

    def _generar_advertencias(self, proposito: str, nivel: str) -> list[str]:
        advertencias = []
        if proposito not in USOS_PERMITIDOS:
            advertencias.append(
                f"El propósito '{proposito}' no está en la lista de usos "
                "explícitamente aprobados. Proceda con cautela y documente el uso."
            )
        if nivel == "sector":
            advertencias.append(
                "Los datos a nivel de sector deben publicarse con contexto "
                "estructural (causas sociales) para evitar estigmatización territorial."
            )
        return advertencias


DISCLAIMER_CIENTIFICO = """
NEUTROOSINT-GYE es una plataforma de diagnóstico estructural comunitario.
Los índices neutrosóficos representan vulnerabilidad estructural agregada,
NO probabilidad de eventos criminales futuros.

Este sistema NO debe usarse para:
  • Despliegue preventivo de fuerzas policiales
  • Vigilancia de individuos o comunidades
  • Discriminación en seguros, crédito o empleo
  • Justificar procesos de gentrificación o desalojo

Para reportar uso indebido: myleyvav@ube.edu.ec
Marco legal: Constitución Ecuador Art. 66 (privacidad), LOPDP 2021.
"""
