#!/usr/bin/env python3
"""Generate Concurso 2026 presentation assets (PPTX + PDF)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECURSOS = ROOT / "RECURSOS"
ARTIFACT = ROOT / "backend" / "ml" / "artifacts" / "randomforest-outbreak-v1.0.0.json"


def _load_metrics() -> dict:
    if ARTIFACT.exists():
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))
    return {}


def _ensure_pptx() -> None:
    try:
        import pptx  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx", "-q"])


def _ensure_fpdf() -> None:
    try:
        import fpdf  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])


def build_pptx(metrics: dict) -> Path:
    from pptx import Presentation
    from pptx.util import Inches, Pt

    validation = metrics.get("validation", {})
    slides_content = [
        (
            "Radar de Brotes",
            "Inteligencia epidemiológica territorial\nConcurso Datos Abiertos Colombia 2026\nEquipo ID 200 · Salud y Bienestar",
        ),
        (
            "Problema",
            "Predecir brotes de enfermedades transmisibles integrando:\n"
            "• Morbilidad (SIVIGILA)\n• Vacunación\n• Calidad del aire (PM2.5)\n• Acceso a servicios de salud\n\n"
            "Objetivo: apoyar prevención y respuesta temprana con revisión humana.",
        ),
        (
            "Fuentes abiertas (datos.gov.co)",
            "• SIVIGILA — casos semanales (dengue, hepatitis, chikungunya…)\n"
            "• Cobertura vacunal pentavalente (DPT-HepB-Hib)\n"
            "• PM2.5 promedio anual municipal (+ fallback SISAIRE)\n"
            "• Indicadores INS: mortalidad y partos institucionales\n"
            "• Catálogo DIVIPOLA para validación territorial",
        ),
        (
            "Arquitectura",
            "Backend FastAPI (DDD) + PostgreSQL + ML explicable\n"
            "Frontend Next.js: mapa, alertas, informe territorial\n"
            "Ingestión programada desde datos.gov.co con trazabilidad\n"
            "Docker Compose para despliegue reproducible",
        ),
        (
            "Modelo de IA — 15 variables",
            "Random Forest + SHAP TreeExplainer\n"
            "Panel: municipio × semana epidemiológica × dengue\n"
            "Features: casos, crecimiento, vacunación, PM2.5, acceso a salud, estacionalidad\n"
            "Validación temporal: entrenamiento ≤2020, prueba ≥2021",
        ),
        (
            "Resultados del modelo",
            f"Muestras de entrenamiento: {metrics.get('training_samples', 'N/A')}\n"
            f"Train / test: {validation.get('train_samples', '—')} / {validation.get('test_samples', '—')}\n"
            f"F1: {validation.get('f1', '—')} · Recall: {validation.get('recall', '—')} · ROC-AUC: {validation.get('roc_auc', '—')}\n\n"
            "Cobertura actual: 20 ciudades principales (~9.000 observaciones curadas)\n"
            "Nota: métricas altas en panel acotado; requiere validación epidemiológica externa.",
        ),
        (
            "Demo en vivo",
            "1. http://localhost:3002/brotes — señal y factores SHAP\n"
            "2. Mapa territorial de alertas\n"
            "3. Informe imprimible /informe\n"
            "4. API OpenAPI: http://localhost:8000/docs",
        ),
        (
            "Impacto y límites",
            "Impacto: priorización territorial, explicabilidad para gestores de salud\n"
            "Límites honestos:\n"
            "• No activa respuestas automáticas\n"
            "• Vacunación replicada desde nivel departamental\n"
            "• PM2.5 solo donde hay estaciones\n"
            "• Cobertura parcial vs todo el territorio nacional",
        ),
    ]

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for title, body in slides_content:
        layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = title
        if slide.placeholders:
            body_shape = slide.placeholders[1]
            body_shape.text = body
            for paragraph in body_shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(20)

    out = RECURSOS / "Presentacion.pptx"
    prs.save(out)
    return out


def build_pdf(metrics: dict) -> Path:
    from fpdf import FPDF

    validation = metrics.get("validation", {})

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 18, 18)

    sections = [
        ("Radar de Brotes - Concurso Datos Abiertos 2026", "Equipo ID 200 - Reto Salud y Bienestar\nPrediccion explicable de brotes con datos abiertos e IA."),
        ("Problema", "Integrar morbilidad, vacunacion, calidad del aire y acceso a salud para apoyar la prevencion y respuesta temprana."),
        ("Fuentes", "SIVIGILA, vacunacion pentavalente, PM2.5, indicadores INS, DIVIPOLA."),
        ("Modelo", f"Random Forest - 15 features - SHAP - {metrics.get('training_samples', 'N/A')} muestras - split temporal train/test {validation.get('train_samples', '-')}/{validation.get('test_samples', '-')}."),
        ("Demo", "Frontend /brotes - /mapa - /informe - API /docs"),
        ("Limites", "Apoyo analitico con revision humana obligatoria. Cobertura parcial territorial."),
    ]

    for title, body in sections:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, title)
        pdf.ln(4)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 7, body)

    out = RECURSOS / "presentacion.pdf"
    pdf.output(str(out))
    return out


def main() -> int:
    RECURSOS.mkdir(parents=True, exist_ok=True)
    metrics = _load_metrics()
    _ensure_pptx()
    _ensure_fpdf()
    pptx_path = build_pptx(metrics)
    pdf_path = build_pdf(metrics)
    print(f"Generated: {pptx_path}")
    print(f"Generated: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
