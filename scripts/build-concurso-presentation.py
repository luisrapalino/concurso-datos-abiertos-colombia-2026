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

TEAM_ID = "200"
TEAM_LEVEL = "Intermedio (IA)"
TEAM_CHALLENGE = "Salud y Bienestar — brotes transmisibles"
REPO_URL = "https://github.com/luisrapalino/concurso-datos-abiertos-colombia-2026"
DEMO_URL = "http://localhost:3002/brotes"
API_URL = "http://localhost:8000/docs"
OBSERVATIONS_COUNT = "~9.000"
CITIES_COUNT = "20"


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


def _slides_content(metrics: dict) -> list[tuple[str, str]]:
    validation = metrics.get("validation", {})
    train = validation.get("train_samples", "—")
    test = validation.get("test_samples", "—")
    f1 = validation.get("f1", "—")
    recall = validation.get("recall", "—")
    roc = validation.get("roc_auc", "—")
    samples = metrics.get("training_samples", "N/A")

    return [
        (
            "Radar de Brotes",
            "Concurso Datos al Ecosistema 2026 · IA para Colombia\n\n"
            f"Equipo ID {TEAM_ID} · Nivel {TEAM_LEVEL}\n"
            f"Reto: {TEAM_CHALLENGE}\n\n"
            "Integrantes:\n"
            "• Líder — luisrapalino88@gmail.com\n"
            "• Participante 2 — Rapalinorokate@gmail.com",
        ),
        (
            "Problema y objetivo",
            "Problema:\n"
            "Los brotes de enfermedades transmisibles requieren detección temprana, "
            "pero la información está dispersa en fuentes abiertas.\n\n"
            "Objetivo:\n"
            "Priorizar municipios con señal de brote integrando morbilidad, vacunación, "
            "calidad del aire y acceso a salud — con IA explicable y revisión humana.",
        ),
        (
            "Datos abiertos",
            "Fuentes (datos.gov.co):\n"
            "• SIVIGILA — casos semanales (dengue, hepatitis, chikungunya…)\n"
            "• Vacunación pentavalente DPT-HepB-Hib\n"
            "• PM2.5 anual municipal (+ fallback SISAIRE)\n"
            "• INS: mortalidad y partos institucionales\n\n"
            "Tratamiento:\n"
            f"{CITIES_COUNT} ciudades · {OBSERVATIONS_COUNT} observaciones curadas · "
            "15 variables ML · validación DIVIPOLA · ingestión trazable en PostgreSQL",
        ),
        (
            "Solución e IA",
            "Plataforma modular (FastAPI + Next.js + Docker):\n"
            "• Ingestión desde datos.gov.co con token Socrata\n"
            "• Modelo Random Forest + SHAP TreeExplainer\n"
            "• Panel: municipio × semana epidemiológica × dengue\n"
            "• Validación temporal: entrenamiento ≤2020, prueba ≥2021\n"
            "• Fallback rule-based auditable si no hay modelo promovido",
        ),
        (
            "Resultados y demo",
            f"Modelo promovido: randomforest-outbreak-v1.0.0\n"
            f"• {samples} muestras de entrenamiento (dengue semanal)\n"
            f"• Split temporal: train {train} / test {test}\n"
            f"• F1 {f1} · Recall {recall} · ROC-AUC {roc}\n"
            "• Cautela: panel acotado; validación epidemiológica externa pendiente\n\n"
            "Demo en vivo:\n"
            f"• {DEMO_URL} — señal y factores SHAP\n"
            "• /mapa — alertas territoriales · /informe — reporte imprimible\n"
            f"• API: {API_URL}",
        ),
        (
            "Impacto",
            "Beneficiarios: gestores de salud pública y vigilancia territorial\n\n"
            "Valor público:\n"
            "• Priorización de territorios antes del pico de casos\n"
            "• Explicación clara de factores (no caja negra)\n"
            "• Reproducible con datos abiertos oficiales\n\n"
            "Sostenibilidad: worker de ingestión, documentación, CI y despliegue Docker",
        ),
        (
            "Repositorio y recursos",
            f"GitHub: {REPO_URL}\n\n"
            "Documentación clave:\n"
            "• README.md — ficha técnica y reproducción\n"
            "• docs/concurso-alignment.md — trazabilidad del reto\n"
            "• docs/data-dictionary.md — 15 variables\n"
            "• docs/ml-evaluation.md — validación y límites\n"
            "• RECURSOS/ — presentación y portada",
        ),
        (
            "Cierre",
            "Frase clave:\n"
            "Priorizamos municipios con riesgo de brote usando datos abiertos "
            "de Colombia e IA explicable.\n\n"
            "Valor diferencial:\n"
            "Integración multifuente + explicabilidad SHAP + plataforma demostrable "
            "en 10 minutos.\n\n"
            "Gracias — preguntas técnicas bienvenidas.",
        ),
    ]


def build_pptx(metrics: dict) -> Path:
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for title, body in _slides_content(metrics):
        layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = title
        if slide.placeholders:
            body_shape = slide.placeholders[1]
            body_shape.text = body
            for paragraph in body_shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(18)

    out = RECURSOS / "Presentacion.pptx"
    prs.save(out)
    return out


def build_pdf(metrics: dict) -> Path:
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 18, 18)

    for title, body in _slides_content(metrics):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, _ascii_safe(title))
        pdf.ln(4)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, _ascii_safe(body))

    out = RECURSOS / "presentacion.pdf"
    pdf.output(str(out))
    return out


def _ascii_safe(text: str) -> str:
    replacements = {
        "—": "-",
        "·": "-",
        "•": "-",
        "…": "...",
        "≤": "<=",
        "≥": ">=",
        "×": "x",
        "ó": "o",
        "í": "i",
        "á": "a",
        "é": "e",
        "ú": "u",
        "ñ": "n",
        "Ó": "O",
        "Í": "I",
        "Á": "A",
        "É": "E",
        "Ú": "U",
        "Ñ": "N",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


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
