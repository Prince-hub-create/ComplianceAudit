import pandas as pd
from backend.models.payroll_model import EmployeePayroll

def parse_payroll_excel(file_path: str):
    df = pd.read_excel(file_path)

    payroll_entries = []
    for _, row in df.iterrows():
        payroll_entries.append(EmployeePayroll(
            employee_code=row.get("Employee Code"),
            employee_name=row.get("Employee Name"),
            uan=row.get("UAN"),
            esic_number=row.get("ESIC Number"),
            designation=row.get("Designation"),
            working_days=row.get("Working Days"),
            basic=row.get("Basic"),
            hra=row.get("HRA"),
            gross=row.get("Gross"),
            deductions=row.get("Deductions"),
            net_salary=row.get("Net Salary"),
            pf_deducted=row.get("PF Deducted"),
            esic_deducted=row.get("ESIC Deducted"),
            overtime=row.get("OT"),
            advance=row.get("Advance Salary Details"),
        ))

    return payroll_entries
