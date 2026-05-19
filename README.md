# NEUTROOSINT-GYE

**Plataforma de Inteligencia de Fuentes Abiertas basada en Lógica Neutrosófica  
para la Caracterización Dinámica de la Violencia Urbana en Guayaquil**

> **Camino B — Diagnóstico Estructural Comunitario**  
> Esta plataforma NO es un sistema de predicción policial.  
> Es un laboratorio comunitario de diagnóstico estructural pluriversal.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io)

---

## Descripción

NEUTROOSINT-GYE integra:

1. **Lógica Neutrosófica SVN** (Smarandache 1998/1999) — tripletas (T, I, F) para representar verdad, indeterminación y falsedad simultáneamente.
2. **Lógica Neutrosófica Paraconsistente Anotada (NPL)** (Leyva-Vázquez & Smarandache 2026) — triple anotación (mu, lambda, I) que distingue evidencia epistemológica de indeterminación ontológica.
3. **N-fsQCA** — análisis configuracional difuso neutrosófico para detectar silenciamiento de drivers estructurales en medios.
4. **OSINT multi-fuente** — integración de noticias, estadísticas oficiales, satélite NASA y análisis LLM.

### El problema central

Los sistemas de caracterización de violencia urbana tradicionales producen un **índice escalar** que:
- Promedia contradicciones entre fuentes → destruye información epistemológica
- No puede representar "barrio bien iluminado + alta violencia de género" simultáneamente
- Facilita usos de predictive policing al simplificar la realidad

NEUTROOSINT-GYE usa el marco **paraconsistente neutrosófico** para **preservar y visibilizar** esas contradicciones.

---

## Arquitectura de 5 capas

```
┌─────────────────────────────────────────────────────────────┐
│                    NEUTROOSINT-GYE v1.0                     │
├────────────────────┬────────────────────────────────────────┤
│   OSINT Collector  │  Fuentes: GNews · INEC · NASA · LLM    │
├────────────────────┴────────────────────────────────────────┤
│  C1 Narrativa     C2 Oficial   C3 Satelital  C4 N-fsQCA    │
│  (20%)            (30%)        (15%)         (20%)          │
│                       C5 Encuesta (15%)                     │
├─────────────────────────────────────────────────────────────┤
│            SVN Core: TIF Triplets + SVNWA                   │
│            NPL Layer: (mu, lambda, I) + NPL-ES              │
├─────────────────────────────────────────────────────────────┤
│              IPVE (Índice Pluriversal Vulnerabilidad)        │
│           Paraconsistency Detector (Hamming distance)        │
├─────────────────────────────────────────────────────────────┤
│              Streamlit Dashboard (7 páginas)                 │
│              Ethical Safeguards (Camino B)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Instalación rápida

```bash
git clone https://github.com/mleyvaz/neutroosint-gye
cd neutroosint-gye
pip install -r requirements.txt
```

Crear `.env`:
```
GNEWS_API_KEY=tu_clave_aqui
OPENROUTER_API_KEY=tu_clave_aqui
```

Ejecutar el dashboard:
```bash
streamlit run src/dashboard.py --server.port 8503
```

### Con Docker

```bash
docker compose up -d
# Dashboard en http://localhost:8503
```

---

## Módulos principales

| Módulo | Descripción |
|--------|-------------|
| `src/neutrosophic_core.py` | TIFTriplet, SVNWA, clasificación de regímenes |
| `src/npl_annotated.py` | NPL: (mu, lambda, I), NPL-ES, embedding phi: LPA→SVN |
| `src/osint_collector.py` | Recolectores multi-fuente (noticias, INEC, NASA) |
| `src/narrative_analyzer.py` | LLM + N-fsQCA pipeline, silenciamiento mediático |
| `src/violence_index.py` | IPVE tríadico, SectorIPVE, informe diagnóstico |
| `src/paraconsistency_detector.py` | Detector Hamming inter-fuente, clasificación |
| `src/ethical_safeguards.py` | Marco ético Camino B, audit log, validación |
| `src/dashboard.py` | Interfaz Streamlit 7 páginas |
| `scripts/daily_collect.py` | Recolección diaria (GitHub Actions) |

---

## Hallazgo principal (caso Urdesa)

> **"Barrio bien iluminado ≠ barrio seguro para todas las personas"**

Los centros formales de Guayaquil (Urdesa, Bolívar, Centro Histórico) muestran
**mayor paraconsistencia**: alta iluminación nocturna (F alto en capa luz) + alta
incidencia de violencia de género (T alto en capa oficial).

Un índice escalar produciría un score "moderado" promediando ambos valores,
**destruyendo** la señal. El marco NPL-Neutrosófico la preserva con:

```
NPL(mu=0.52, λ=0.45, I=0.23) → Estado: NPL-PARA (paraconsistencia epistémica)
```

---

## Marco legal y ético

- **Constitución Ecuador** Art. 66 (derecho a la privacidad)
- **LOPDP 2021** (Ley Orgánica de Protección de Datos Personales)
- **Camino B**: no venta a aseguradoras, inmobiliarias ni fuerzas de seguridad
- Granularidad mínima: sector (nunca manzana ni individuo)
- Audit log automático de toda exportación

---

## Publicaciones asociadas

1. Leyva-Vázquez, M., Cevallos-Torres, L., Guijarro Rodríguez, A., Iturburu-Salvador, M., & Smarandache, F. (2026). *LLM + Neutrosophic fsQCA: Inter-Narrative Causal Consistency and Paraconsistent Detection in Media Accounts of Urban Violence in Guayaquil*. WorldS4 2026, Springer LNNS. (Submission #304)

2. Leyva-Vázquez, M. & Smarandache, F. (2026). *Neutrosophic Paraconsistent Logic: Evidence Degrees, Ontological Indeterminacy, and Scientific Evidence Synthesis*. (En revisión — NCML)

3. Leyva-Vázquez, M. (2026). *Guayaquil Neutro-Safe Digital Twin*. IEEE ETCM 2026. (Enviado 10-may-2026)

---

## Citar este trabajo

```bibtex
@software{neutroosint_gye_2026,
  author    = {Leyva-Vázquez, Maikel Yelandi},
  title     = {{NEUTROOSINT-GYE}: Open Source Intelligence Platform
               based on Neutrosophic Logic for Urban Violence
               Characterization in Guayaquil},
  year      = {2026},
  url       = {https://github.com/mleyvaz/neutroosint-gye},
  license   = {MIT}
}
```

---

## Contacto

**Dr. Maikel Yelandi Leyva-Vázquez**  
Universidad Bolivariana del Ecuador (UBE) | Universidad de Guayaquil  
Editor-in-Chief: Neutrosophic Sets and Systems (NSS) | NCML  
myleyvav@ube.edu.ec | mleyvaz@gmail.com  
ORCID: 0000-0001-7911-5879

---

*Desarrollado como laboratorio comunitario de diagnóstico estructural pluriversal.*  
*"El marco paraconsistente visibiliza lo que el índice escalar oculta."*
