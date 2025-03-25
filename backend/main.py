from fastapi import FastAPI, Depends, HTTPException, Security, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sys
import os
from typing import List
import pandas as pd  # ✅ Added pandas for Excel processing
from pydantic import BaseModel
from backend.database import SessionLocal, engine
from backend import crud, models
from backend.schemas import VendorCreate, UserCreate
from typing import List, Literal

# Create Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create JWT token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# Extract user role from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        user = crud.get_user_by_id(db, int(user_id))  # ✅ Fixed Indentation
        if user is None:
            raise credentials_exception
        return {"user_id": user.id, "role": user.role}
    except JWTError:
        raise credentials_exception


# ✅ Test Database Connection API
@app.get("/test-db")
def test_db_connection(db: Session = Depends(lambda: SessionLocal())):
    try:
        db.execute("SELECT 1")  # Simple test query
        return {"message": "✅ Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")        

# CLIENT DASHBOARD APIs
@app.get("/client/vendors/")
def get_client_vendors(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Access denied")

    # ✅ Fetch vendors only from the site the client is assigned to
    vendors = db.query(models.Vendor).filter(models.Vendor.site_name == user["site_name"]).all()
    
    return vendors

@app.get("/client/vendor-documents/{vendor_id}")
def get_vendor_documents(vendor_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Access denied")

    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id, models.Vendor.site_name == user["site_name"]).first()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found or not in your site")

    return crud.get_vendor_documents(db, vendor_id)

@app.get("/client/audit-report/{vendor_id}")
def get_audit_report(vendor_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_audit_report(db, vendor_id)

# INTERNAL DASHBOARD APIs
@app.get("/internal/vendors/")
def get_all_vendors(site_name: str = None, po_number: str = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "internal":
        raise HTTPException(status_code=403, detail="Access denied")

    query = db.query(models.Vendor)

    # ✅ Filter by Site (if provided)
    if site_name:
        query = query.filter(models.Vendor.site_name == site_name)

    # ✅ Filter by PO/WO/SO Number (if provided)
    if po_number:
        query = query.filter(models.Vendor.po_number == po_number)

    return query.all()

@app.get("/internal/vendor-audit/{vendor_id}")
def get_vendor_audit(vendor_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "internal":
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_vendor_audit(db, vendor_id)

@app.post("/internal/modify-audit/{audit_id}")
def modify_audit_observations(audit_id: int, new_observations: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "internal":
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.modify_audit(db, audit_id, new_observations)

# New API: Vendor Audit Status
@app.get("/vendor/audit-status/")
def get_vendor_audit_status(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "vendor":
        raise HTTPException(status_code=403, detail="Access denied")

    audit_status = db.query(models.Audit).filter(models.Audit.vendor_id == user["user_id"]).all()
    observations = db.query(models.Observations).filter(models.Observations.vendor_id == user["user_id"]).all()

    return {
        "audit_status": audit_status,
        "observations": observations  # ✅ Vendors can see their own observations
    }

# New API: Download Compliance Documents
@app.get("/download/document/{document_id}")
def download_document(document_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = os.path.join("uploads", document.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=document.filename)


# ✅ Test Route
@app.get("/")
def root():
    return {"message": "Labor Compliance Audit API is running!"}

# ✅ Define User Registration Schema
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    po_wo_so_number: str
    site_name: str
    company_name: str
    mobile_number: str
    role: Literal["vendor", "client", "internal"]  # ✅ Role selection

# ✅ SIGNUP ROUTE
@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        po_wo_so_number=user.po_wo_so_number,
        site_name=user.site_name,
        company_name=user.company_name,
        mobile_number=user.mobile_number,
        role=user.role  # ✅ Store user role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

    return {"message": "User registered successfully", "user_id": new_user.id, "access_token": token}

# ✅ Define Login Schema
class LoginRequest(BaseModel):
    email: str
    password: str

# ✅ LOGIN ROUTE (Returns User Role)
@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    
    if not existing_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not pwd_context.verify(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(existing_user.id), "role": existing_user.role})

    return {
        "access_token": token, 
        "token_type": "bearer",
        "role": existing_user.role  # ✅ Send role to frontend
    }

# ✅ Secure Role-Based Dashboards
@app.get("/dashboard/vendor/")
def vendor_dashboard(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "vendor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "message": "✅ Vendor Dashboard Loaded",
        "vendor_name": "Example Vendor",
        "vendor_email": "vendor@example.com"
    }

@app.get("/dashboard/client/")
def client_dashboard(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "message": "✅ Client Dashboard Loaded",
        "client_name": "Example Client",
        "client_email": "client@example.com"
    }

@app.get("/dashboard/internal/")
def internal_dashboard(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "internal":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "message": "✅ Internal Dashboard Loaded",
        "internal_name": "Example Internal User",
        "internal_email": "internal@example.com"
    }
    
# ✅ Create uploads directory if not exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Upload Compliance Documents
@app.post("/upload-files/")
async def upload_files(
    vendorName: str = Form(...),
    vendorAddress: str = Form(...),
    month: str = Form(...),
    principalEmployer: str = Form(...),
    employerAddress: str = Form(...),
    siteName: str = Form(...),
    siteAddress: str = Form(...),
    poNumber: str = Form(...),
    remarks: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files received")

        saved_files = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_files.append(file.filename)

        return {"message": "Files uploaded successfully!", "files": saved_files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")

# ✅ Extract Required Columns from Excel
REQUIRED_COLUMNS = [
    "Employee Code", "Employee Name", "UAN", "ESIC Number", "Designation",
    "Working Days", "Basic", "HRA", "Any Other Allowance", "PF Wages", "PF Contribution",
    "ESIC Contribution", "Gross", "Deductions", "Net Salary", "OT", "Advance Salary",
    "Bank Transfer Reference", "Bonus Detail", "Bonus Paid Date", "Leave Record",
    "Leave Encashment", "Fine Detail", "Damage & Loss Detail"
]

# ✅ Upload and Process Excel Files
@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())

        df = pd.read_excel(file_path, engine="openpyxl")

        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return {"error": f"Missing columns: {', '.join(missing_columns)}"}

        extracted_data = df[REQUIRED_COLUMNS].to_dict(orient="records")

        for employee in extracted_data:
            # ✅ Convert 'bonus_paid_date' safely
            bonus_paid_date = employee["Bonus Paid Date"]
            if isinstance(bonus_paid_date, str) and bonus_paid_date.strip() == "-":
                bonus_paid_date = None  # ✅ Store NULL instead of "-"

            elif isinstance(bonus_paid_date, str):  
                try:
                    bonus_paid_date = datetime.strptime(bonus_paid_date, "%Y-%m-%d").date()
                except ValueError:
                    bonus_paid_date = None  # ✅ Handle incorrect date format safely

            db_employee = models.EmployeeRecord(
                employee_code=employee["Employee Code"],
                employee_name=employee["Employee Name"],
                uan=employee["UAN"],
                esic_number=employee["ESIC Number"],
                designation=employee["Designation"],
                working_days=employee["Working Days"],
                basic_salary=employee["Basic"], 
                hra=employee["HRA"],
                any_other_allowance=employee["Any Other Allowance"],  # ✅ Must match models.py
                pf_wages=employee["PF Wages"],
                pf_contribution=employee["PF Contribution"],  # ✅ Fixed Column
                esic_contribution=employee["ESIC Contribution"],  # ✅ Fixed Column
                gross=employee["Gross"],  # ✅ Ensure this key matches the database
                deductions=employee["Deductions"],
                net_salary=employee["Net Salary"],
                ot=employee["OT"],
                advance_salary=employee["Advance Salary"],
                bank_transfer_reference=employee["Bank Transfer Reference"],
                bonus_detail=employee["Bonus Detail"],
                bonus_paid_date=bonus_paid_date,  # ✅ Ensure safe insertion
                leave_record=employee["Leave Record"],
                leave_encashment=employee["Leave Encashment"],
                fine_detail=employee["Fine Detail"],
                damage_loss_detail=employee["Damage & Loss Detail"]
            )
            db.add(db_employee)

        db.commit()

        return {"message": "File processed successfully", "data": extracted_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ✅ Print registered routes properly
@app.on_event("startup")
async def startup_event():
    for route in app.routes:
        print(route.path)

print("FastAPI is running with registered routes:", app.routes)
