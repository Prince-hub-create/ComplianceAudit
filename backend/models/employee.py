from sqlalchemy import Column, Integer, String, Numeric, Date
from backend.database import Base  # Ensure this import is correct

class EmployeeRecord(Base):
    __tablename__ = "employee_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    uan = Column(String(50))
    esic_number = Column(String(50))
    designation = Column(String(100))
    working_days = Column(Integer)
    basic_salary = Column(Numeric)
    hra = Column(Numeric)
    any_other_allowance = Column(Numeric, nullable=True)
    pf_contribution = Column(Numeric)
    esic_contribution = Column(Numeric)
    gross = Column(Numeric, nullable=False)
    deductions = Column(Numeric)
    ot = Column(Numeric)
    advance_salary = Column(Numeric)
    bank_transfer_reference = Column(String(100))
    bonus_detail = Column(String(100))
    bonus_paid_date = Column(Date)
    leave_record = Column(String(100))
    leave_encashment = Column(String(100))
    fine_detail = Column(String(100))
    damage_loss_detail = Column(String(100))
    pf_wages = Column(Numeric)
    net_salary = Column(Numeric)
