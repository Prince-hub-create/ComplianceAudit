import pandas as pd
from fpdf import FPDF

def validate_minimum_wage(df, min_wage):
    """Check if wages meet minimum wage requirements."""
    df['Minimum Wage Compliance'] = df['Basic'].fillna(0) >= min_wage
    return df

def validate_pf_compliance(df):
    """Check PF deductions (12% of Basic) and ensure UAN is valid."""
    df['PF Compliance'] = df.apply(
        lambda row: (row['PF Deduction'] >= row['Basic'] * 0.12) if pd.notnull(row['UAN']) else False, axis=1
    )
    return df

def validate_esic_compliance(df):
    """Check ESIC contributions for employees earning below ₹21,000."""
    df['ESIC Compliance'] = df.apply(
        lambda row: (row['Gross'] < 21000 and row['ESIC Deduction'] >= row['Gross'] * 0.0075) or (row['Gross'] >= 21000),
        axis=1
    )
    return df

def validate_overtime(df):
    """Check if overtime wages are correctly calculated."""
    df['OT Compliance'] = df.apply(
        lambda row: row['OT Pay'] >= row['OT Hours'] * (row['Basic'] / 30 / 8 * 1.5) if pd.notnull(row['OT Hours']) else True,
        axis=1
    )
    return df

def validate_salary_payment(df):
    """Check if salary was paid via bank and on time (before the 10th)."""
    df['Payment Date'] = pd.to_numeric(df['Payment Date'], errors='coerce')
    df['Salary Payment Compliance'] = (df['Payment Mode'] == 'Bank Transfer') & (df['Payment Date'].between(1, 10, inclusive="both"))
    return df

def match_pf_challan(wage_register, pf_challan):
    """Compare PF contributions in wage register with PF challan."""
    merged = pd.merge(wage_register, pf_challan, on='UAN', suffixes=('_Register', '_Challan'), how='left')
    merged['PF Match'] = merged['PF Deduction_Register'].fillna(0) == merged['PF Deduction_Challan'].fillna(0)
    return merged[['Employee Name', 'UAN', 'PF Deduction_Register', 'PF Deduction_Challan', 'PF Match']]

def match_esic_challan(wage_register, esic_challan):
    """Compare ESIC contributions in wage register with ESIC challan."""
    merged = pd.merge(wage_register, esic_challan, on='ESIC Number', suffixes=('_Register', '_Challan'), how='left')
    merged['ESIC Match'] = merged['ESIC Deduction_Register'].fillna(0) == merged['ESIC Deduction_Challan'].fillna(0)
    return merged[['Employee Name', 'ESIC Number', 'ESIC Deduction_Register', 'ESIC Deduction_Challan', 'ESIC Match']]

def generate_audit_report(df, filename="audit_report.pdf"):
    """Generate a structured PDF audit report with compliance results."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Labor Compliance Audit Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "Employee Name", border=1, align='C')
    pdf.cell(40, 10, "Min Wage", border=1, align='C')
    pdf.cell(30, 10, "PF", border=1, align='C')
    pdf.cell(30, 10, "ESIC", border=1, align='C')
    pdf.cell(30, 10, "OT", border=1, align='C')
    pdf.cell(30, 10, "Salary", border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(40, 10, row['Employee Name'], border=1, align='C')
        pdf.cell(40, 10, "✔️" if row['Minimum Wage Compliance'] else "❌", border=1, align='C')
        pdf.cell(30, 10, "✔️" if row['PF Compliance'] else "❌", border=1, align='C')
        pdf.cell(30, 10, "✔️" if row['ESIC Compliance'] else "❌", border=1, align='C')
        pdf.cell(30, 10, "✔️" if row['OT Compliance'] else "❌", border=1, align='C')
        pdf.cell(30, 10, "✔️" if row['Salary Payment Compliance'] else "❌", border=1, align='C')
        pdf.ln()

    pdf.output(filename)
    print(f"Audit report generated: {filename}")

# Example Usage
if __name__ == "__main__":
    # Sample DataFrames (Replace with actual Excel read)
    employee_data = pd.DataFrame({
        'Employee Name': ['A', 'B', 'C'],
        'UAN': [123, 456, None],
        'ESIC Number': [987654, 654321, 321987],
        'Basic': [12000, 15000, 8000],
        'Gross': [18000, 20000, 9000],
        'PF Deduction': [1440, 1800, 960],
        'ESIC Deduction': [135, 150, 68],
        'OT Hours': [5, 10, 2],
        'OT Pay': [750, 1500, 200],
        'Payment Mode': ['Bank Transfer', 'Cash', 'Bank Transfer'],
        'Payment Date': ['7', '12', '10']
    })

    pf_challan_data = pd.DataFrame({
        'UAN': [123, 456, 789],
        'PF Deduction': [1440, 1300, 900]
    })

    esic_challan_data = pd.DataFrame({
        'ESIC Number': [987654, 654321, 321987],
        'ESIC Deduction': [135, 150, 250]
    })

    # Apply Validations
    employee_data = validate_minimum_wage(employee_data, min_wage=10000)
    employee_data = validate_pf_compliance(employee_data)
    employee_data = validate_esic_compliance(employee_data)
    employee_data = validate_overtime(employee_data)
    employee_data = validate_salary_payment(employee_data)

    # Match PF & ESIC Contributions
    pf_mismatch = match_pf_challan(employee_data, pf_challan_data)
    esic_mismatch = match_esic_challan(employee_data, esic_challan_data)

    # Generate Audit Report
    generate_audit_report(employee_data)
