from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class PayrollCompliance(Base):
    __tablename__ = "payroll_compliance"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    uan = Column(String, nullable=True)
    esic_number = Column(String, nullable=True)
    designation = Column(String, nullable=False)
    gross_salary = Column(Float, nullable=False)
    pf_deduction = Column(Float, default=0)
    esic_deduction = Column(Float, default=0)
    ot_hours = Column(Float, default=0)
    ot_pay = Column(Float, default=0)
    working_days = Column(Integer, nullable=False)
    bank_transfer_reference = Column(String, nullable=True)
    compliance_issues = Column(String, nullable=True)  # Stores issues as a JSON string

