import io
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .ml_model import predict_dengue, get_current_metrics
from .models import ClimateData, Notification

def generate_report_pdf(db: Session, year: int, month: int, inspector_name: str) -> bytes:
    """Generate a PDF report in memory and return the raw bytes."""
    # 1. Fetch climate data for the prediction context
    climate = db.query(ClimateData).filter(
        ClimateData.year == year,
        ClimateData.month == month
    ).first()
    
    if climate:
        min_t, max_t, hum, rain = climate.min_temp, climate.max_temp, climate.humidity, climate.rainfall
    else:
        # Fallback averages if specific data doesn't exist
        min_t, max_t, hum, rain = 22.0, 31.0, 78.0, 10.0
        
    # 2. Predict cases and risk
    predicted_cases, risk_level = predict_dengue(db, min_t, max_t, hum, rain)
    metrics = get_current_metrics(db)
    
    # 3. Calculate Resource Allocations
    beds_needed = max(5, int(predicted_cases * 0.15))
    paracetamol_units = max(100, int(predicted_cases * 20))
    iv_fluids_units = max(50, int(predicted_cases * 5))
    platelet_units = max(10, int(predicted_cases * 0.5))
    
    # 4. Fetch recent alerts for this target period
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month - 1]
    alerts = db.query(Notification).filter(
        Notification.message.like(f"%{month_name} {year}%")
    ).limit(3).all()
    
    # Create file-like buffer
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#334155'),
        leading=13
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#334155'),
        leading=12
    )

    story = []
    
    # Header
    story.append(Paragraph("AI-Based Dengue Outbreak Prediction & Early Warning System", title_style))
    story.append(Paragraph("Dengue Outbreak Prediction & Early Warning Report", subtitle_style))
    
    # Metadata Table
    report_id = f"DPR-DHAKA-{year}{month:02d}-{int(datetime.utcnow().timestamp()) % 1000:03d}"
    meta_data = [
        [
            Paragraph(f"<b>Report ID:</b> {report_id}", meta_style),
            Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%d-%b-%Y, %I:%M %p')}", meta_style)
        ],
        [
            Paragraph(f"<b>Coverage Area:</b> Dhaka Metropolitan (DSCC/DNCC)", meta_style),
            Paragraph(f"<b>Target Period:</b> {month_name} {year}", meta_style)
        ],
        [
            Paragraph(f"<b>Prepared By:</b> {inspector_name} (Public Health Inspector)", meta_style),
            Paragraph("", meta_style) # Empty column
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # Executive Summary Section
    story.append(Paragraph("1. Executive Summary", section_heading))
    risk_color = '#EF4444' if risk_level == 'HIGH' else '#F59E0B' if risk_level == 'MEDIUM' else '#10B981'
    summary_html = (
        f"This report presents a predictive risk snapshot for the Dhaka region based on climate factors.<br/>"
        f"• <b>Overall Risk Level:</b> <font color='{risk_color}'><b>{risk_level}</b></font><br/>"
        f"• <b>Predicted Cases (Next 4 weeks):</b> <b>{predicted_cases:,} cases</b><br/>"
        f"• <b>Model Performance ($R^2$ Score):</b> {metrics.r2:.2f}"
    )
    story.append(Paragraph(summary_html, body_style))
    story.append(Spacer(1, 10))
    
    # Weather & Environmental Data Section
    story.append(Paragraph("2. Weather & Environmental Context", section_heading))
    weather_data = [
        ["Meteorological Variable", "Average Value", "Significance for Mosquito Breeding"],
        ["Avg Minimum Temperature", f"{min_t:.1f} °C", "Supports larval development rate"],
        ["Avg Maximum Temperature", f"{max_t:.1f} °C", "High temp accelerates viral replication inside vector"],
        ["Avg Humidity", f"{hum:.1f} %", "Higher humidity prolongs adult mosquito lifespan"],
        ["Total Rainfall", f"{rain:.1f} mm", "Creates breeding sites in stagnant water pool pools"]
    ]
    weather_table = Table(weather_data, colWidths=[160, 100, 280])
    weather_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F1F5F9')),
    ]))
    story.append(weather_table)
    story.append(Spacer(1, 10))
    
    # Recommended Resource Allocation Section
    story.append(Paragraph("3. Recommended Resource Allocation (Surge Planning)", section_heading))
    resource_data = [
        ["Resource Category", "Estimated Needs", "Purpose / Specific Utility"],
        ["Hospital Beds Needed", f"+{beds_needed} beds", "Ensure ward bed capacities are ready"],
        ["Paracetamol Stock", f"+{paracetamol_units:,} units", "First-line fever management medicine"],
        ["IV Fluid Stocks (Normal Saline)", f"+{iv_fluids_units:,} units", "Manage dehydration in dengue hemorrhagic fever"],
        ["Blood & Platelet Units", f"+{platelet_units:,} units", "For severe cases requiring transfusion"]
    ]
    resource_table = Table(resource_data, colWidths=[160, 100, 280])
    resource_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F1F5F9')),
    ]))
    story.append(resource_table)
    story.append(Spacer(1, 10))
    
    # Early Warning Alerts Issued Section
    story.append(Paragraph("4. Simulated Early-Warning Alerts Logs", section_heading))
    if alerts:
        alerts_data = [["Timestamp", "Channel", "Recipient", "Notification Status"]]
        for a in alerts:
            alerts_data.append([
                a.timestamp.strftime("%Y-%m-%d %H:%M"),
                a.channel,
                a.recipient,
                a.status
            ])
        alerts_table = Table(alerts_data, colWidths=[120, 70, 250, 100])
        alerts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(alerts_table)
    else:
        story.append(Paragraph("No warnings were triggered or sent for this period (Risk level Low).", body_style))
    story.append(Spacer(1, 15))
    
    # Disclaimer
    disclaimer_text = (
        "<b>Disclaimer:</b> Predictions are generated using a multiple linear regression algorithm fed by "
        "historical climate trends. These numbers represent estimates to support health administrative "
        "planning and should be verified against field entomological surveys and clinical reports."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle(
        'Disclaimer', parent=body_style, fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor('#64748B')
    )))
    
    # Build Document
    doc.build(story)
    
    # Extract bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
