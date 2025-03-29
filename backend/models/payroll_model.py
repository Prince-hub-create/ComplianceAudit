from pydantic import BaseModel
from typing import List, Optional
from backend.models.base import Base  # Import Base

class EmployeePayroll(BaseModel):
    employee_code: str
    employee_name: str
    uan: Optional[str]
    esic_number: Optional[str]
    designation: str
    working_days: int
    basic: float
    hra: float
    gross: float
    deductions: float
    net_salary: float
    pf_deducted: Optional[float]
    esic_deducted: Optional[float]
    overtime: Optional[float]
    advance: Optional[float]

class PayrollRequest(BaseModel):
    company_name: str
    month: str
    payroll_data: List[EmployeePayroll]
