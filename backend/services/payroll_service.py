import json
from backend.models.payroll import PayrollCompliance
from sqlalchemy.orm import Session

# Compliance Constants
MIN_WAGE = 10000
PF_THRESHOLD = 15000
ESIC_THRESHOLD = 21000

def check_payroll_compliance(db: Session, payroll_data: dict):
    issues = []

    # Convert numeric fields safely
    try:
        gross_salary = float(payroll_data.get("gross_salary", 0))
        pf_deduction = float(payroll_data.get("pf_deduction", 0))
        esic_deduction = float(payroll_data.get("esic_deduction", 0))
        ot_hours = float(payroll_data.get("ot_hours", 0))
        ot_pay = float(payroll_data.get("ot_pay", 0))
        working_days = int(payroll_data.get("working_days", 0))
    except ValueError:
        return {"error": "Invalid numeric values in payroll data"}

    # Minimum Wage Check
    if gross_salary < MIN_WAGE:
        issues.append(f"Gross salary ({gross_salary}) is below the minimum wage ({MIN_WAGE}).")

    # PF Compliance Check
    if gross_salary >= PF_THRESHOLD and pf_deduction == 0:
        issues.append("PF deduction is missing for an employee above PF threshold.")

    # ESIC Compliance Check
    if gross_salary <= ESIC_THRESHOLD and esic_deduction == 0:
        issues.append("ESIC deduction is missing for an employee under ESIC limit.")

    # Overtime Pay Check
    if ot_hours > 0 and ot_pay == 0:
        issues.append("Overtime pay is missing despite overtime hours recorded.")

    # Weekly Off Compliance (Muster Roll Check)
    if working_days > 26:
        issues.append("No weekly off provided (working days exceed 26).")

    # Salary Payment Proof Check
    if not payroll_data.get("bank_transfer_reference"):
        issues.append("Salary payment proof is missing (Bank Transfer Reference).")

    # Save to Database
    compliance_record = PayrollCompliance(
        employee_name=payroll_data.get("employee_name", "Unknown"),
        uan=payroll_data.get("uan", ""),
        esic_number=payroll_data.get("esic_number", ""),
        designation=payroll_data.get("designation", ""),
        gross_salary=gross_salary,
        pf_deduction=pf_deduction,
        esic_deduction=esic_deduction,
        ot_hours=ot_hours,
        ot_pay=ot_pay,
        working_days=working_days,
        bank_transfer_reference=payroll_data.get("bank_transfer_reference", ""),
        compliance_issues=json.dumps(issues)
    )

    db.add(compliance_record)
    db.commit()
    db.refresh(compliance_record)

    return compliance_record
