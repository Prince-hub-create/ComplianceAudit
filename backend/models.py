from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, TIMESTAMP, ARRAY, Date, Float, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base  # ✅ Correct absolute import
import datetime
from sqlalchemy.sql import func
from sqlalchemy import Enum
from pydantic import BaseModel
from typing import List

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    po_wo_so_number = Column(String, nullable=True)
    site_name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    
    # ✅ Add Role Column (Vendor, Client, Internal)
    role = Column(Enum("vendor", "client", "internal", name="user_roles"), nullable=False)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    vendor = relationship("Vendor", back_populates="documents")

# Audit Model
class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(255), nullable=False)
    site_name = Column(String(255), nullable=False)
    audit_month = Column(Date, nullable=False)
    status = Column(String(50), default="Pending")
    uploaded_documents = Column(ARRAY(Text))  # Store list of document URLs
    created_at = Column(TIMESTAMP, server_default=func.now())

    observations = relationship("Observation", back_populates="audit")

# Observation Model
class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"))
    comment = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    audit = relationship("Audit", back_populates="observations")

# Vendor Model
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    documents = relationship("Document", back_populates="vendor")  # ✅ Ensure relationships are correctly defined
    
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
    any_other_allowance = Column(Numeric, nullable=True)  # ✅ Ensure this exists
    pf_contribution = Column(Numeric)
    esic_contribution = Column(Numeric)
    gross = Column(Numeric, nullable=False)  # ✅ Ensure this column exists
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

class RegisterRequest(BaseModel):
    state: str
    register_type: str
    excel_file: str  # Path to uploaded Excel file

class WCBocwDetails(Base):
    __tablename__ = "wc_bocw_details"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, index=True)
    site_address = Column(String)
    wc_policy_number = Column(String)
    wc_expiry_date = Column(Date)
    wc_employee_count = Column(Integer)
    bocw_registration_number = Column(String)
    bocw_employee_count = Column(Integer)
    compliance_status = Column(Boolean, default=True)  # True = Compliant, False = Non-compliant