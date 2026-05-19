"""
Script de recolección diaria ejecutado por GitHub Actions.
Actualiza data/processed/ con los datos OSINT más recientes.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.osint_collector import OSINTOrchestrator
from src.violence_index import IPVECalculator, generar_informe_diagnostico
from src.npl_annotated import anotar_osint_con_npl

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    logger.info("=== NEUTROOSINT-GYE Daily Collect ===")
    logger.info(f"Fecha UTC: {datetime.utcnow().isoformat()}")

    orquestador = OSINTOrchestrator()
    registros = orquestador.recolectar_todo()
    total = sum(len(v) for v in registros.values())
    logger.info(f"Registros recolectados: {total}")

    calculador = IPVECalculator()
    sectores = calculador.calcular(registros)
    logger.info(f"Sectores calculados: {len(sectores)}")

    anotaciones_npl = anotar_osint_con_npl(registros)
    logger.info(f"Anotaciones NPL: {len(anotaciones_npl)}")

    informe = generar_informe_diagnostico(sectores)
    informe["fecha_actualizacion"] = datetime.utcnow().isoformat()

    salida = {
        "sectores": [s.to_dict() for s in sectores],
        "anotaciones_npl": anotaciones_npl,
        "informe": informe,
    }

    out_file = OUTPUT_DIR / f"ipve_{datetime.utcnow().strftime('%Y%m%d')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    latest = OUTPUT_DIR / "latest.json"
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    logger.info(f"Datos guardados en {out_file} y {latest}")
    logger.info("=== Completado ===")


if __name__ == "__main__":
    main()
