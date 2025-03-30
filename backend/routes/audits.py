from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Audit, Observation
from typing import List
from pydantic import BaseModel
from datetime import date
from database import get_db
import pandas as pd

router = APIRouter()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class AuditBase(BaseModel):
    vendor_name: str
    site_name: str
    audit_month: date

class AuditResponse(AuditBase):
    id: int
    status: str
    uploaded_documents: List[str] = []

    class Config:
        orm_mode = True  # Allows returning SQLAlchemy objects as Pydantic models

# API to get all audits
@router.get("/audits", response_model=List[AuditResponse])
def get_audits(db: Session = Depends(get_db)):
    audits = db.query(Audit).all()
    return [AuditResponse(
        id=audit.id,
        vendor_name=audit.vendor_name,
        site_name=audit.site_name,
        audit_month=audit.audit_month,
        status=audit.status,
        uploaded_documents=audit.uploaded_documents or []  # Ensure it's always a list
    ) for audit in audits]

# API to get audit details
@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return AuditResponse(
        id=audit.id,
        vendor_name=audit.vendor_name,
        site_name=audit.site_name,
        audit_month=audit.audit_month,
        status=audit.status,
        uploaded_documents=audit.uploaded_documents or []
    )

# API to add an observation
class ObservationRequest(BaseModel):
    comment: str

class ObservationResponse(BaseModel):
    id: int
    audit_id: int
    comment: str

    class Config:
        orm_mode = True

@router.post("/audits/{audit_id}/observations", response_model=ObservationResponse)
def add_observation(audit_id: int, request: ObservationRequest, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    observation = Observation(audit_id=audit_id, comment=request.comment)
    db.add(observation)
    db.commit()
    db.refresh(observation)  # Ensure we return the latest data

    return observation

router = APIRouter()

@router.post("/process-excel/")
async def process_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = pd.read_excel(io.BytesIO(file.file.read()))

        # Required columns in the Excel file
        required_columns = ["Employee Code", "Employee Name", "Basic", "Gross", "PF Deduction", "ESIC Deduction", "OT Hours"]
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing column: {col}")

        # Compliance Checks
        observations = []
        for _, row in df.iterrows():
            if row["PF Deduction"] == 0:
                observations.append(f"PF not deducted for {row['Employee Name']} ({row['Employee Code']})")
            if row["ESIC Deduction"] == 0 and row["Gross"] < 21000:
                observations.append(f"ESIC missing for {row['Employee Name']} ({row['Employee Code']})")
            if row["OT Hours"] > 50:
                observations.append(f"Excess overtime for {row['Employee Name']} ({row['Employee Code']})")

        # Store audit report in DB
        new_report = AuditReport(compliance_status="Completed", observations=observations)
        db.add(new_report)
        db.commit()
        return {"message": "Audit processed successfully", "observations": observations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-audit-report/{vendor_id}")
def get_audit_report(vendor_id: int, db: Session = Depends(get_db)):
    report = db.query(AuditReport).filter(AuditReport.vendor_id == vendor_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="No audit report found")
    return {"compliance_status": report.compliance_status, "observations": report.observations}

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@router.get("/download-audit-report/{vendor_id}")
def download_audit_report(vendor_id: int, db: Session = Depends(get_db)):
    report = db.query(AuditReport).filter(AuditReport.vendor_id == vendor_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Audit report not found")

    # Create PDF
    pdf_path = f"reports/audit_report_{vendor_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Audit Report")
    c.drawString(100, 730, f"Vendor ID: {vendor_id}")
    c.drawString(100, 710, f"Compliance Status: {report.compliance_status}")
    
    y_position = 690
    for obs in report.observations:
        c.drawString(100, y_position, f"- {obs}")
        y_position -= 20

    c.save()
    return {"message": "PDF generated", "pdf_path": pdf_path}
