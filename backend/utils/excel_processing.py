import pandas as pd
import yaml
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import os

def load_templates():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
    template_path = os.path.join(base_dir, "..", "templates", "register_formats.yaml")

    with open(template_path, "r") as file:
        return file.read()  # Or use yaml.safe_load(file) if it's a YAML file


TEMPLATES = load_templates()

def generate_register(state: str, register_type: str, input_file: str, output_folder: str):
    """Generate registers dynamically based on state format and export as Excel and PDF"""

    if state not in TEMPLATES:
        raise ValueError(f"State format not found: {state}")

    format_columns = TEMPLATES[state].get(register_type, {}).get("columns", [])

    if not format_columns:
        raise ValueError(f"Register type {register_type} not found for state {state}")

    # Load input Excel
    df = pd.read_excel(input_file)

    # Select required columns dynamically
    df_selected = df[format_columns]

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save to Excel
    excel_output_file = f"{output_folder}/{register_type}_{state}.xlsx"
    df_selected.to_excel(excel_output_file, index=False)

    # Convert Excel to PDF
    pdf_output_file = f"{output_folder}/{register_type}_{state}.pdf"
    convert_excel_to_pdf(df_selected, pdf_output_file)

    return {"Excel": excel_output_file, "PDF": pdf_output_file}

def convert_excel_to_pdf(df: pd.DataFrame, output_file: str):
    """Convert a Pandas DataFrame to a PDF file"""

    c = canvas.Canvas(output_file, pagesize=landscape(letter))
    width, height = landscape(letter)

    data = [df.columns.tolist()] + df.values.tolist()

    # Define table with data
    table = Table(data, colWidths=80, rowHeights=20)

    # Apply table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    # Position table in PDF
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, height - 50 - len(df) * 20)

    # Save PDF
    c.save()
