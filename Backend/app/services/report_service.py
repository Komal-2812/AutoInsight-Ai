import json
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from app.config import settings

def generate_pdf_report(dataset_id: str, analysis: dict) -> str:
    """Generate PDF report and return file path."""
    path = os.path.join(settings.REPORT_DIR, f"report_{dataset_id}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AutoInsight AI — Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Dataset ID: {dataset_id}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(analysis.get("summary", ""), styles["Normal"]))
    story.append(Spacer(1, 12))

    # KPIs
    story.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
    kpi_data = [["Metric", "Value", "Unit"]]
    for kpi in analysis.get("kpis", []):
        kpi_data.append([kpi.get("label", ""), str(kpi.get("value", "")), kpi.get("unit", "")])
    if len(kpi_data) > 1:
        t = Table(kpi_data)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t)
    story.append(Spacer(1, 12))

    # Insights
    story.append(Paragraph("AI Insights", styles["Heading2"]))
    for insight in analysis.get("insights", []):
        story.append(Paragraph(f"• {insight}", styles["Normal"]))
    story.append(Spacer(1, 12))

    doc.build(story)
    return path