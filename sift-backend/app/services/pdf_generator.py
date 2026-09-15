import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_court_report(evidence_data: dict, custody_events: list, findings: list) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=10)
    normal_style = styles['Normal']

    # --- HEADER ---
    elements.append(Paragraph("SIFT DIGITAL FORENSICS PLATFORM", title_style))
    elements.append(Paragraph("COURT-ADMISSIBLE CHAIN OF CUSTODY & ANALYSIS DOSSIER", ParagraphStyle('SubTitle', parent=styles['Heading3'], alignment=1)))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WAT", normal_style))
    elements.append(Spacer(1, 20))

    # --- 1. EVIDENCE PROFILE ---
    elements.append(Paragraph("1. EVIDENCE PROFILE", styles['Heading2']))
    profile_data = [
        ["Filename:", Paragraph(evidence_data.get("filename", "N/A"), normal_style)],
        ["SHA-256 Baseline:", Paragraph(evidence_data.get("sha256_hash", "N/A"), normal_style)],
        ["Current Status:", Paragraph(f"<b>{evidence_data.get('status', 'N/A')}</b>", normal_style)]
    ]
    t_profile = Table(profile_data, colWidths=[120, 390])
    t_profile.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_profile)
    elements.append(Spacer(1, 20))

    # --- 2. DCoC LEDGER ---
    elements.append(Paragraph("2. DIGITAL CHAIN OF CUSTODY (DCoC)", styles['Heading2']))
    coc_data = [["Timestamp", "Officer ID", "Action", "Location"]]
    
    for event in custody_events:
        ts = event.get('timestamp')
        # Neo4j timestamps are in milliseconds
        date_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M') if ts else "Unknown"
        
        coc_data.append([
            Paragraph(date_str, normal_style),
            Paragraph(event.get("officer_id", "N/A"), normal_style),
            Paragraph(f"<b>{event.get('action', 'N/A')}</b>", normal_style),
            Paragraph(event.get("location", "N/A"), normal_style)
        ])
        
    t_coc = Table(coc_data, colWidths=[90, 100, 160, 160])
    t_coc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(t_coc)
    elements.append(Spacer(1, 20))

    # --- 3. FORENSIC FINDINGS ---
    elements.append(Paragraph("3. AUTOMATED FORENSIC FINDINGS", styles['Heading2']))
    if not findings:
        elements.append(Paragraph("No automated analysis findings recorded for this asset.", normal_style))
    else:
        for f in findings:
            elements.append(Paragraph(f"<b>[{f.get('type')}] - Status: {f.get('status')}</b>", normal_style))
            elements.append(Paragraph(f.get('statement', ''), normal_style))
            elements.append(Spacer(1, 10))
    
    # --- 4. ATTESTATION ---
    elements.append(Spacer(1, 40))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("CERTIFICATION OF AUTHENTICITY", styles['Heading3']))
    elements.append(Paragraph("I hereby certify that the digital evidence tracking and mathematical analyses detailed in this dossier were maintained inside the SIFT cryptographic framework in accordance with ISO 27037 standards. The SHA-256 integrity baseline and chronological ledger are immutable.", normal_style))
    elements.append(Spacer(1, 50))
    elements.append(Paragraph("___________________________________________________", normal_style))
    elements.append(Paragraph("Lead Forensic Examiner / System Operator", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer