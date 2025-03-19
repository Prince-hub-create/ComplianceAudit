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

# API to get all audits
@router.get("/audits", response_model=List[AuditResponse])
def get_audits(db: Session = Depends(get_db)):
    return db.query(Audit).all()

# API to get audit details
@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit

# API to add an observation
class ObservationRequest(BaseModel):
    comment: str

@router.post("/audits/{audit_id}/observations")
def add_observation(audit_id: int, request: ObservationRequest, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    observation = Observation(audit_id=audit_id, comment=request.comment)
    db.add(observation)
    db.commit()
    return {"message": "Observation added successfully"}
