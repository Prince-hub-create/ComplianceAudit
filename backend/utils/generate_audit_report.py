from fpdf import FPDF

class AuditReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(200, 10, "Compliance Audit Report", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, "Page " + str(self.page_no()), align="C")

def generate_audit_report(violations, output_file="audit_report.pdf"):
    pdf = AuditReport()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    if violations:
        pdf.cell(200, 10, "Non-Compliance Issues Found:", ln=True, align="L")
        pdf.ln(5)
        for idx, violation in enumerate(violations, 1):
            pdf.cell(0, 10, f"{idx}. {violation}", ln=True, align="L")
    else:
        pdf.cell(200, 10, "All records are compliant.", ln=True, align="L")

    pdf.output(output_file)

# Example Usage
if __name__ == "__main__":
    issues = ["John Doe: Basic salary below minimum wage", "Jane Smith: PF deduction incorrect"]
    generate_audit_report(issues)
