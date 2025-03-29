from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import pandas as pd
import io
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.services.payroll_service import check_payroll_compliance

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-payroll/")
async def upload_payroll(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        required_columns = {
            "Employee Name", "UAN", "ESIC Number", "Designation", 
            "Gross Salary", "PF Deduction", "ESIC Deduction", 
            "OT Hours", "OT Pay", "Working Days", "Bank Transfer Reference"
        }

        # Check for missing columns
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing_columns}")

        results = []
        for _, row in df.iterrows():
            payroll_data = {col.lower().replace(" ", "_"): row[col] for col in required_columns}
            
            # Check and validate compliance
            compliance_result = check_payroll_compliance(db, payroll_data)

            if "error" in compliance_result:
                raise HTTPException(status_code=400, detail=compliance_result["error"])

            results.append(compliance_result)

        return {"status": "success", "compliance_results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
