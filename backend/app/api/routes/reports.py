import io
import os
import logging
import pandas as pd
import numpy as np
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse

# Matplotlib headless setup
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)
router = APIRouter()

# Numbered canvas subclass to handle page numbers and headers dynamically
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1e3a8a"))
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.drawString(54, 750, "NUCLEAR FUEL COMPLEX (NFC) • SECURITY AUDIT DIVISION")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(558, 750, "Insider Threat Assessment & Anomaly Telemetry Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer (On all pages)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#991b1b"))
        self.drawString(54, 40, "RESTRICTED / CONFIDENTIAL")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(185, 40, "•   NFC Internal Telemetry   •   Government of India")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)
        self.restoreState()


@router.get("/export/csv")
def export_csv(type: str = Query(..., description="Report type: profile, anomalies, or risk")):
    """
    Stream and export raw CSV security files from disk.
    """
    filename_map = {
        "profile": "final_security_profile.csv",
        "anomalies": "anomaly_report.csv",
        "risk": "risk_scores.csv"
    }
    
    if type not in filename_map:
        raise HTTPException(status_code=400, detail="Invalid report type. Choose: 'profile', 'anomalies', or 'risk'")
    
    # Locate target file
    possible_dirs = ["../data/reports/", "data/reports/", "../data/reports/", "data/reports/"]
    target_file = None
    for d in possible_dirs:
        test_path = os.path.join(d, filename_map[type])
        if os.path.exists(test_path):
            target_file = test_path
            break
            
    if not target_file:
        raise HTTPException(status_code=404, detail=f"Source CSV report file '{filename_map[type]}' not found on security vault.")
        
    return FileResponse(
        path=target_file,
        media_type="text/csv",
        filename=filename_map[type]
    )


@router.get("/export/pdf")
def export_pdf(request: Request):
    """
    Generate and download a beautifully styled PDF security telemetry report with charts.
    """
    try:
        data_service = request.app.state.data_service
    except Exception as e:
        logger.error(f"Failed to access DataService: {e}")
        raise HTTPException(status_code=500, detail="Security database connection failure.")

    if data_service.users_df.empty:
        raise HTTPException(status_code=404, detail="No security logs loaded to build reports.")

    # 1. Prepare Matplotlib Charts in memory
    plt.close('all') # Clear any residues
    
    # Chart A: Risk Distribution (Donut Pie)
    risk_counts = data_service.users_df['risk_level'].value_counts()
    risk_levels_ordered = ['Low', 'Medium', 'High', 'Critical']
    risk_values = [risk_counts.get(level, 0) for level in risk_levels_ordered]
    risk_colors = ['#22c55e', '#f59e0b', '#ea580c', '#ef4444']
    
    fig_a, ax_a = plt.subplots(figsize=(4.5, 2.5))
    wedges, texts, autotexts = ax_a.pie(
        risk_values, 
        labels=risk_levels_ordered, 
        autopct='%1.1f%%',
        startangle=90, 
        colors=risk_colors, 
        pctdistance=0.75,
        textprops=dict(color="#1e293b", size=7, weight="bold")
    )
    plt.setp(autotexts, size=6, weight="bold")
    # Draw center circle to make it a donut chart
    centre_circle = plt.Circle((0,0),0.55,fc='white')
    ax_a.add_artist(centre_circle)
    ax_a.axis('equal')  
    plt.title("User Risk Level Distribution", fontsize=9, color="#1e3a8a", weight="bold")
    buf_a = io.BytesIO()
    plt.savefig(buf_a, format='png', dpi=200, bbox_inches='tight')
    buf_a.seek(0)
    plt.close(fig_a)

    # Chart B: Department Summary (Horizontal Bars)
    dept_counts = data_service.users_df.groupby('department').agg(
        total_users=('user_id', 'size'),
        anomalies=('anomaly_label', lambda x: sum(x == 'Suspicious'))
    ).reset_index()
    dept_counts = dept_counts.sort_values('anomalies', ascending=True).tail(6) # Show top 6
    
    fig_b, ax_b = plt.subplots(figsize=(4.5, 2.5))
    y_pos = np.arange(len(dept_counts))
    bar_width = 0.35
    
    ax_b.barh(y_pos - bar_width/2, dept_counts['total_users'], bar_width, label='Total Users', color='#475569')
    ax_b.barh(y_pos + bar_width/2, dept_counts['anomalies'], bar_width, label='Anomalies', color='#ef4444')
    
    ax_b.set_yticks(y_pos)
    # Truncate department names for PDF layout space
    clean_depts = [d.split(" - ")[-1][:15] for d in dept_counts['department']]
    ax_b.set_yticklabels(clean_depts, fontsize=7)
    ax_b.tick_params(axis='x', labelsize=7)
    ax_b.legend(fontsize=6, loc="lower right")
    plt.title("Threat Anomalies by Department", fontsize=9, color="#1e3a8a", weight="bold")
    buf_b = io.BytesIO()
    plt.savefig(buf_b, format='png', dpi=200, bbox_inches='tight')
    buf_b.seek(0)
    plt.close(fig_b)

    # Chart C: Login & Device Trends (Subplots Timeline)
    fig_c, (ax_c1, ax_c2) = plt.subplots(2, 1, figsize=(9.5, 3.2), sharex=True)
    
    login_days = [p['day'] for p in data_service.login_trends_data]
    login_counts = [p['count'] for p in data_service.login_trends_data]
    ax_c1.plot(login_days, login_counts, color='#3b5bdb', linewidth=1)
    ax_c1.set_title("Daily Logon Event Trends", fontsize=8, color="#1e3a8a", weight="bold")
    ax_c1.tick_params(axis='y', labelsize=6)
    ax_c1.get_xaxis().set_visible(False)
    
    device_days = [p['day'] for p in data_service.device_trends_data]
    device_counts = [p['count'] for p in data_service.device_trends_data]
    ax_c2.fill_between(device_days, device_counts, color='#8b5cf6', alpha=0.3)
    ax_c2.plot(device_days, device_counts, color='#8b5cf6', linewidth=1)
    ax_c2.set_title("Daily USB Connection Trends", fontsize=8, color="#1e3a8a", weight="bold")
    ax_c2.tick_params(axis='both', labelsize=6)
    ax_c2.get_xaxis().set_ticks([]) # Hide dense dates
    
    plt.suptitle("500+ Day Timeline Telemetry Analysis", fontsize=9, color="#1e293b", weight="bold")
    buf_c = io.BytesIO()
    plt.savefig(buf_c, format='png', dpi=200, bbox_inches='tight')
    buf_c.seek(0)
    plt.close(fig_c)

    # 2. Build PDF Document with ReportLab Flowables
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom typography style templates
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#991b1b'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white
    )

    table_cell_body = ParagraphStyle(
        'TableCellBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1e293b')
    )
    
    table_cell_body_bold = ParagraphStyle(
        'TableCellBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1e293b')
    )

    elements = []

    # --- PAGE 1: TITLE & EXECUTIVE SUMMARY ---
    elements.append(Paragraph("NUCLEAR FUEL COMPLEX (NFC)", ParagraphStyle('GovHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=2)))
    elements.append(Paragraph("DEPARTMENT OF ATOMIC ENERGY • GOVERNMENT OF INDIA", ParagraphStyle('SubGovHeader', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#64748b'), spaceAfter=12)))
    
    elements.append(Paragraph("Insider Threat Telemetry & Anomaly Report", title_style))
    elements.append(Paragraph("SECURITY AUDIT CYBER SCANNERS   •   RESTRICTED CIRCULATION", subtitle_style))
    
    # Executive Summary Box
    summary_text = (
        "<b>Executive Summary:</b> This report presents the data intelligence results of the NFC Cyber Threat Auditor "
        "and Anomaly Detection Engine. Using scikit-learn's Isolation Forest ML model, user activity logs (including daily logon timings, "
        "off-hours login ratios, and USB connect events) have been parsed to flag anomalous behaviors. High-risk outliers "
        "have been scored and categorized. The telemetry indicates a controlled environment with specific isolated profiles "
        "requiring supervisory audit review. The metrics below represent the state as of June 2026."
    )
    elements.append(Paragraph(summary_text, ParagraphStyle('SummaryText', parent=body_style, fontSize=9.5, leading=14, backColor=colors.HexColor('#f8fafc'), borderColor=colors.HexColor('#cbd5e1'), borderWidth=0.5, borderPadding=8, spaceAfter=15)))
    
    # Overview metrics table
    overview = data_service.get_dashboard_overview()
    stats_data = [
        [Paragraph("<b>Security Telemetry Parameter</b>", table_cell_header), Paragraph("<b>Count / Value</b>", table_cell_header), Paragraph("<b>Assessment Context</b>", table_cell_header)],
        [Paragraph("Total Monitored Employees", table_cell_body), Paragraph(f"{overview['total_users']:,}", table_cell_body_bold), Paragraph("Full database registry count", table_cell_body)],
        [Paragraph("Flagged Anomalous Users", table_cell_body), Paragraph(f"{overview['anomalies_detected']}", table_cell_body_bold), Paragraph("Outliers flagged by Isolation Forest (5% contamination)", table_cell_body)],
        [Paragraph("High Risk Category Profiles", table_cell_body), Paragraph(f"{overview['high_risk_users']}", table_cell_body_bold), Paragraph("Behavioral scoring: High (Score 51 - 75)", table_cell_body)],
        [Paragraph("Critical Threat Category Profiles", table_cell_body), Paragraph(f"{overview['critical_users']}", table_cell_body_bold), Paragraph("Immediate Action Required: Critical (Score 76 - 100)", table_cell_body)]
    ]
    
    stats_table = Table(stats_data, colWidths=[150, 80, 274])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
    ]))
    
    elements.append(Paragraph("1. Core Security Indicators", h1_style))
    elements.append(stats_table)
    elements.append(Spacer(1, 15))

    # Matplotlib charts for Page 1 bottom
    charts_table_data = [
        [Image(buf_a, width=2.4*72, height=1.35*72), Image(buf_b, width=2.4*72, height=1.35*72)]
    ]
    charts_table = Table(charts_table_data, colWidths=[252, 252])
    charts_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(Paragraph("2. Risk & Department Summary Distribution", h1_style))
    elements.append(charts_table)
    
    elements.append(PageBreak())

    # --- PAGE 2: TIMELINE CHARTS & CRITICAL THREAT USERS ---
    elements.append(Paragraph("3. Temporal Telemetry Analysis", h1_style))
    elements.append(Paragraph("The charts below show daily trends for login activity and USB device connection telemetry across a 500+ day timeline window. Spikes represent potential audit trigger points.", body_style))
    elements.append(Image(buf_c, width=7.0*72, height=2.3*72))
    elements.append(Spacer(1, 12))

    # Filter critical threat users: Suspicious + Critical risk level
    users_df = data_service.users_df
    critical_threat_users = users_df[
        (users_df['anomaly_label'] == 'Suspicious') & 
        (users_df['risk_level'] == 'Critical')
    ].sort_values('risk_score', ascending=False)
    
    # High threat users: Suspicious + High risk level
    high_threat_users = users_df[
        (users_df['anomaly_label'] == 'Suspicious') & 
        (users_df['risk_level'] == 'High')
    ].sort_values('risk_score', ascending=False)

    # 4. Render Threat Tables
    elements.append(Paragraph("4. High-Threat Behavioral Profiles", h1_style))
    
    if high_threat_users.empty:
        elements.append(Paragraph("No users currently flagged under High-Threat (High Risk + Suspicious anomaly).", body_style))
    else:
        high_table_data = [
            [Paragraph("<b>User ID</b>", table_cell_header), Paragraph("<b>Name</b>", table_cell_header), Paragraph("<b>Department</b>", table_cell_header), Paragraph("<b>Designated Role</b>", table_cell_header), Paragraph("<b>Risk Score</b>", table_cell_header), Paragraph("<b>Clearance</b>", table_cell_header)]
        ]
        for _, r in high_threat_users.iterrows():
            high_table_data.append([
                Paragraph(f"<b>{r['user_id']}</b>", table_cell_body_bold),
                Paragraph(r['name'] if pd.notna(r['name']) else "N/A", table_cell_body),
                Paragraph(r['department'] if pd.notna(r['department']) else "N/A", table_cell_body),
                Paragraph(r['role'] if pd.notna(r['role']) else "N/A", table_cell_body),
                Paragraph(f"{r['risk_score']:.1f}", table_cell_body_bold),
                Paragraph(r['security_status'], table_cell_body)
            ])
        
        high_table = Table(high_table_data, colWidths=[60, 100, 140, 100, 50, 54])
        high_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ea580c')), # High Threat Color: Orange
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ]))
        elements.append(high_table)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("5. Critical-Threat Behavioral Profiles", h1_style))
    elements.append(Paragraph("Profiles flagged with Critical Risk Level (score 76-100) and Suspicious anomaly label. These cases require immediate clearance auditing.", body_style))
    
    if critical_threat_users.empty:
        elements.append(Paragraph("No users currently flagged under Critical Threat.", body_style))
    else:
        # Show top 25 users to fit nicely in PDF
        top_critical = critical_threat_users.head(22)
        
        crit_table_data = [
            [Paragraph("<b>User ID</b>", table_cell_header), Paragraph("<b>Name</b>", table_cell_header), Paragraph("<b>Department</b>", table_cell_header), Paragraph("<b>Role</b>", table_cell_header), Paragraph("<b>Risk Score</b>", table_cell_header), Paragraph("<b>Security Status</b>", table_cell_header)]
        ]
        for _, r in top_critical.iterrows():
            crit_table_data.append([
                Paragraph(f"<b>{r['user_id']}</b>", table_cell_body_bold),
                Paragraph(r['name'] if pd.notna(r['name']) else "N/A", table_cell_body),
                Paragraph(r['department'] if pd.notna(r['department']) else "N/A", table_cell_body),
                Paragraph(r['role'] if pd.notna(r['role']) else "N/A", table_cell_body),
                Paragraph(f"{r['risk_score']:.1f}", table_cell_body_bold),
                Paragraph(r['security_status'], table_cell_body)
            ])
            
        crit_table = Table(crit_table_data, colWidths=[60, 100, 140, 100, 50, 54])
        crit_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ef4444')), # Critical Color: Red
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')])
        ]))
        elements.append(crit_table)
        
        if len(critical_threat_users) > 22:
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"<i>Note: First 22 of {len(critical_threat_users)} critical threat users displayed. Please download the CSV data report for the complete queue list.</i>", ParagraphStyle('NoteStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, textColor=colors.HexColor('#64748b'))))

    # Build PDF
    doc.build(elements, canvasmaker=NumberedCanvas)
    pdf_buffer.seek(0)

    # Return stream
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=nfc_insider_threat_report.pdf"}
    )
