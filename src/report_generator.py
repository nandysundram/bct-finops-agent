"""
Report Generator
Creates PDF and DOCX reports with cost analysis and recommendations
"""

from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class ReportGenerator:
    def __init__(self):
        """Initialize report generator"""
        self.severity_colors = {
            'Critical': colors.red,
            'High': colors.orange,
            'Medium': colors.yellow,
            'Low': colors.lightgreen
        }
    
    def generate_pdf(
        self,
        cost_data: Dict,
        ri_data: Dict,
        recommendations: List[Dict],
        output_path: str
    ):
        """Generate PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title with BCT Branding
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            alignment=1  # Center
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#003d7a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph("BCT FINOPS TOOL", title_style))
        story.append(Paragraph("Cloud Financial Operations & Optimization Report", subtitle_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Cost (6 months)', f"${cost_data['total_cost']:,.2f}"],
            ['Monthly Average', f"${cost_data['total_cost']/6:,.2f}"],
            ['Total Recommendations', str(len(recommendations))],
            ['Critical/High Priority', str(sum(1 for r in recommendations if r.get('severity') in ['Critical', 'High']))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # RI Analysis
        story.append(Paragraph("Reserved Instance Analysis", styles['Heading2']))
        ri_recommendations = ri_data['recommendations'].get('Recommendations', [])
        story.append(Paragraph(f"Active RIs: {len(ri_data['current_ris'])}", styles['Normal']))
        story.append(Paragraph(f"RI Purchase Recommendations: {len(ri_recommendations)}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Cost Optimization Recommendations", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        for idx, rec in enumerate(recommendations, 1):
            # Recommendation header
            rec_title = f"{idx}. {rec.get('title', 'Recommendation')}"
            story.append(Paragraph(rec_title, styles['Heading3']))
            
            # Details table
            rec_data = [
                ['Severity', rec.get('severity', 'N/A')],
                ['Timeline', rec.get('timeline', 'N/A')],
                ['Estimated Savings', rec.get('estimated_savings', 'N/A')],
                ['Impact', rec.get('impact', 'N/A')]
            ]
            
            rec_table = Table(rec_data, colWidths=[1.5*inch, 4*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10)
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Description
            story.append(Paragraph(f"<b>Description:</b> {rec.get('description', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Implementation steps
            if 'steps' in rec and rec['steps']:
                story.append(Paragraph("<b>Implementation Steps:</b>", styles['Normal']))
                for step in rec['steps']:
                    story.append(Paragraph(f"• {step}", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(story)
    
    def generate_docx(
        self,
        cost_data: Dict,
        ri_data: Dict,
        recommendations: List[Dict],
        output_path: str
    ):
        """Generate DOCX report"""
        doc = Document()
        
        # Title with BCT Branding
        title = doc.add_heading('BCT FINOPS TOOL', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].font.color.rgb = RGBColor(0, 102, 204)
        
        subtitle = doc.add_paragraph('Cloud Financial Operations & Optimization Report')
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle.runs[0].font.size = Pt(14)
        subtitle.runs[0].font.color.rgb = RGBColor(0, 61, 122)
        
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph()
        
        # Executive Summary
        doc.add_heading('Executive Summary', 1)
        
        summary_table = doc.add_table(rows=5, cols=2)
        summary_table.style = 'Light Grid Accent 1'
        
        summary_data = [
            ('Metric', 'Value'),
            ('Total Cost (6 months)', f"${cost_data['total_cost']:,.2f}"),
            ('Monthly Average', f"${cost_data['total_cost']/6:,.2f}"),
            ('Total Recommendations', str(len(recommendations))),
            ('Critical/High Priority', str(sum(1 for r in recommendations if r.get('severity') in ['Critical', 'High'])))
        ]
        
        for row_idx, (label, value) in enumerate(summary_data):
            row = summary_table.rows[row_idx]
            row.cells[0].text = label
            row.cells[1].text = value
            
            if row_idx == 0:
                for cell in row.cells:
                    cell.paragraphs[0].runs[0].font.bold = True
        
        doc.add_paragraph()
        
        # RI Analysis
        doc.add_heading('Reserved Instance Analysis', 1)
        ri_recommendations = ri_data['recommendations'].get('Recommendations', [])
        doc.add_paragraph(f"Active RIs: {len(ri_data['current_ris'])}")
        doc.add_paragraph(f"RI Purchase Recommendations: {len(ri_recommendations)}")
        doc.add_paragraph()
        
        # Recommendations
        doc.add_page_break()
        doc.add_heading('Cost Optimization Recommendations', 1)
        
        for idx, rec in enumerate(recommendations, 1):
            # Recommendation title
            doc.add_heading(f"{idx}. {rec.get('title', 'Recommendation')}", 2)
            
            # Details table
            details_table = doc.add_table(rows=4, cols=2)
            details_table.style = 'Light List Accent 1'
            
            details_data = [
                ('Severity', rec.get('severity', 'N/A')),
                ('Timeline', rec.get('timeline', 'N/A')),
                ('Estimated Savings', rec.get('estimated_savings', 'N/A')),
                ('Impact', rec.get('impact', 'N/A'))
            ]
            
            for row_idx, (label, value) in enumerate(details_data):
                row = details_table.rows[row_idx]
                row.cells[0].text = label
                row.cells[1].text = value
                row.cells[0].paragraphs[0].runs[0].font.bold = True
                
                # Color code severity
                if label == 'Severity':
                    severity = rec.get('severity', 'N/A')
                    if severity == 'Critical':
                        row.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 0, 0)
                    elif severity == 'High':
                        row.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 165, 0)
            
            doc.add_paragraph()
            
            # Description
            desc_para = doc.add_paragraph()
            desc_para.add_run('Description: ').bold = True
            desc_para.add_run(rec.get('description', 'N/A'))
            
            # Implementation steps
            if 'steps' in rec and rec['steps']:
                steps_para = doc.add_paragraph()
                steps_para.add_run('Implementation Steps:').bold = True
                
                for step in rec['steps']:
                    doc.add_paragraph(step, style='List Bullet')
            
            doc.add_paragraph()
        
        # Save document
        doc.save(output_path)
