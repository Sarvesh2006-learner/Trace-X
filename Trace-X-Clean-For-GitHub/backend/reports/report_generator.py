from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from backend.config import Config

def generate_report(evidence, analysis):
    Config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = Config.REPORT_DIR / f"TRACE-X_Evidence_{evidence.id}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = [
        Paragraph("TRACE-X Digital Forensic Analysis Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Forensic indicators are analytical aids and must be independently reviewed by an authorized investigator.", styles["BodyText"]),
        Spacer(1, 12)
    ]
    data = [
        ["Field", "Value"],
        ["Evidence ID", str(evidence.id)],
        ["Case ID", evidence.case_id],
        ["Original filename", evidence.original_filename],
        ["File type", evidence.file_type or ""],
        ["File size", str(evidence.file_size)],
        ["SHA-256", evidence.sha256_hash],
        ["Content hash", evidence.content_hash or "N/A"],
        ["Image pHash", evidence.image_hash or "N/A"],
        ["Exact duplicate", str(analysis.duplicate_found)],
        ["Content match", str(analysis.content_match_found)],
        ["Semantic score", str(analysis.semantic_score if analysis.semantic_score is not None else "N/A")],
        ["Image similarity", str(analysis.image_similarity if analysis.image_similarity is not None else "N/A")],
        ["Morphing indicator", analysis.morphing_indicator],
    ]
    table = Table(data, colWidths=[150, 360])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph("Findings", styles["Heading2"]))
    import json
    for finding in json.loads(analysis.findings or "[]"):
        story.append(Paragraph("• " + finding, styles["BodyText"]))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 12))
    story.append(Paragraph("TRACE-X does not declare authenticity or forgery solely from AI, hashing, ELA, pHash, or similarity scores. Results should be corroborated using chain-of-custody records and human forensic examination.", styles["BodyText"]))
    doc.build(story)
    return str(path)
