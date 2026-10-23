#!/usr/bin/env python3
"""Gera PDF a partir de relatorio-auditoria-seguranca.md (dados embutidos do último audit)."""

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent
PDF_PATH = OUT_DIR / "relatorio-auditoria-seguranca.pdf"

SEV_COLORS = {
    "critica": colors.HexColor("#B91C1C"),
    "alta": colors.HexColor("#EA580C"),
    "media": colors.HexColor("#D97706"),
    "baixa": colors.HexColor("#2563EB"),
    "forte": colors.HexColor("#059669"),
}

FINDINGS = [
    ("Média", "static/index.html:72-74", "XSS via innerHTML na agenda (título da reserva)"),
    ("Baixa", "app/main.py:144-163", "Cancelamento por ID sem auth"),
    ("Informativa", "app/main.py", "API aberta (PRD sem login)"),
    ("Informativa", "app/main.py:64-76", "POST /api/salas sem restrição"),
]

COUNTS = {"Crítica": 0, "Alta": 0, "Média": 1, "Baixa": 1, "Informativa": 2}


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "Relatório de Auditoria de Segurança — Reserva de Salas")
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main() -> None:
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Relatório de Auditoria de Segurança", styles["Title"]))
    story.append(Paragraph("Reserva de Salas (gerado/)", styles["h2"]))
    story.append(Paragraph(f"Data: {date.today().isoformat()}", styles["Normal"]))
    story.append(
        Paragraph(
            "Escopo: FastAPI + SQLite + UI estática. Metodologia: 5 categorias (skill revisao-seguranca).",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Resumo executivo", styles["h2"]))
    count_data = [[k, str(v)] for k, v in COUNTS.items()]
    t = Table([["Severidade", "Qtd"]] + count_data, colWidths=[8 * cm, 3 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Achados (amostra verificada)", styles["h2"]))
    rows = [["Severidade", "Local", "Descrição"]] + [[a, b, c] for a, b, c in FINDINGS]
    t2 = Table(rows, colWidths=[2.5 * cm, 4.5 * cm, 8 * cm])
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    story.append(t2)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Pontos fortes", styles["h2"]))
    story.append(
        Paragraph(
            "SQL parametrizado; validação Pydantic; sem segredos no repositório; regras em business.py.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Recomendações P1", styles["h2"]))
    story.append(
        Paragraph("Eliminar innerHTML na agenda ou sanitizar entradas da API na UI.", styles["Normal"])
    )

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"PDF gerado: {PDF_PATH}")


if __name__ == "__main__":
    main()
