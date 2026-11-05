import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_certificate_pdf(student_name, student_id_code, course_title, course_code,
                             category_name, duration_weeks, attendance_pct,
                             final_score, grade, certificate_code, issue_date_str,
                             trainer_name="Assigned Trainer", output_filepath=None):
    """
    Generates a professional institutional landscape certificate using ReportLab.
    Outputs to a file path if provided, otherwise returns raw PDF bytes.
    """
    buffer = BytesIO()
    
    # 11 x 8.5 inches landscape
    page_width, page_height = landscape(letter)
    c = canvas.Canvas(output_filepath if output_filepath else buffer, pagesize=landscape(letter))
    
    # Background subtle tint
    c.setFillColor(colors.HexColor('#FCFDFE'))
    c.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    
    # Outer decorative border (Institutional Navy Blue)
    c.setStrokeColor(colors.HexColor('#0B2545'))
    c.setLineWidth(4)
    c.rect(20, 20, page_width - 40, page_height - 40)
    
    # Inner decorative border (Warm Gold)
    c.setStrokeColor(colors.HexColor('#C99700'))
    c.setLineWidth(1.5)
    c.rect(26, 26, page_width - 52, page_height - 52)
    
    # Corner flourishes
    corner_size = 15
    c.setLineWidth(1)
    for x, y in [(26, 26), (page_width - 26, 26), (26, page_height - 26), (page_width - 26, page_height - 26)]:
        dx = corner_size if x < page_width / 2 else -corner_size
        dy = corner_size if y < page_height / 2 else -corner_size
        c.line(x, y + dy, x + dx, y)

    # Institutional Header Banner
    c.setFillColor(colors.HexColor('#153C2A'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(page_width / 2, page_height - 42, 
                        "KALINGA INSTITUTE OF SOCIAL SCIENCES (KISS) • VOCATIONAL TRAINING MANAGEMENT SYSTEM")
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.HexColor('#A9573D'))
    c.drawCentredString(page_width / 2, page_height - 52,
                        "BHUBANESWAR, ODISHA, INDIA • DIRECTORATE OF VOCATIONAL SKILL DEVELOPMENT")
    
    # Certificate Title Header
    c.setFillColor(colors.HexColor('#0B2545'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(page_width / 2, page_height - 85, "CERTIFICATE OF ACHIEVEMENT")
    
    c.setFillColor(colors.HexColor('#C99700'))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(page_width / 2, page_height - 102, "VOCATIONAL SKILL TRAINING & CAPACITY BUILDING PROGRAM")

    # Thin Divider Line
    c.setStrokeColor(colors.HexColor('#CBD5E1'))
    c.setLineWidth(0.8)
    c.line(page_width / 2 - 180, page_height - 112, page_width / 2 + 180, page_height - 112)

    # Presentation text
    c.setFillColor(colors.HexColor('#4A5568'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(page_width / 2, page_height - 135, "This is to certify that")

    # Student Name (Prominent)
    c.setFillColor(colors.HexColor('#1E293B'))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_width / 2, page_height - 165, student_name.upper())

    # Student Identification Details
    c.setFillColor(colors.HexColor('#475569'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_width / 2, page_height - 185, f"Student Identification No: {student_id_code}")

    # Completion Statement
    c.setFillColor(colors.HexColor('#334155'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(page_width / 2, page_height - 215,
                        "has successfully completed the prescribed curriculum and practical assessments for the vocational course")

    # Course Title
    c.setFillColor(colors.HexColor('#0F172A'))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - 245, course_title)

    # Category and Course Code
    c.setFillColor(colors.HexColor('#64748B'))
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_width / 2, page_height - 262, f"Domain: {category_name}  |  Course Code: {course_code}  |  Duration: {duration_weeks} Weeks")

    # Performance Metrics Box
    box_x = page_width / 2 - 200
    box_y = page_height - 330
    c.setFillColor(colors.HexColor('#F8FAFC'))
    c.setStrokeColor(colors.HexColor('#E2E8F0'))
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, 400, 48, 6, fill=1, stroke=1)

    c.setFillColor(colors.HexColor('#1E293B'))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(box_x + 25, box_y + 28, "Attendance Recorded:")
    c.drawString(box_x + 165, box_y + 28, "Assessment Average:")
    c.drawString(box_x + 310, box_y + 28, "Final Grade:")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor('#047857'))
    c.drawString(box_x + 25, box_y + 12, f"{attendance_pct}% (Satisfactory)")
    c.drawString(box_x + 165, box_y + 12, f"{final_score}% (Passed)")
    c.setFillColor(colors.HexColor('#B45309'))
    c.drawString(box_x + 310, box_y + 12, f"Grade {grade}")

    # Verification and Date details
    c.setFillColor(colors.HexColor('#64748B'))
    c.setFont("Helvetica", 9)
    c.drawString(60, page_height - 370, f"Date of Issue: {issue_date_str}")
    c.drawString(60, page_height - 384, f"Certificate ID: {certificate_code}")
    c.drawString(60, page_height - 398, "Status: Verified & Authenticated in KISS-VTMS Registry")

    # Signatures
    # Trainer
    c.setStrokeColor(colors.HexColor('#94A3B8'))
    c.setLineWidth(1)
    c.line(page_width - 340, page_height - 380, page_width - 200, page_height - 380)
    c.setFillColor(colors.HexColor('#1E293B'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(page_width - 270, page_height - 394, trainer_name)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#64748B'))
    c.drawCentredString(page_width - 270, page_height - 406, "Vocational Course Trainer")

    # Administrator
    c.setStrokeColor(colors.HexColor('#94A3B8'))
    c.line(page_width - 170, page_height - 380, page_width - 50, page_height - 380)
    c.setFillColor(colors.HexColor('#1E293B'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(page_width - 110, page_height - 394, "Program Director")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor('#64748B'))
    c.drawCentredString(page_width - 110, page_height - 406, "KISS VTMS Administrator")

    # Finalize canvas
    c.showPage()
    c.save()
    
    if output_filepath:
        return output_filepath
    
    buffer.seek(0)
    return buffer.getvalue()
