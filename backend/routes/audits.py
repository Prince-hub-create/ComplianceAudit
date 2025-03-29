from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Audit, Observation
from typing import List
from pydantic import BaseModel
from datetime import date

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
