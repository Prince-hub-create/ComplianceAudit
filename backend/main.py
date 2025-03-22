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

# ✅ Create Database Tables if not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],   
)

# ✅ Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Secret key for JWT
SECRET_KEY = "your_secret_key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Function to create JWT token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Test Route
@app.get("/")
def root():
    return {"message": "Labor Compliance Audit API is running!"}

# ✅ SIGNUP ROUTE
@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = pwd_context.hash(user.password)
        new_user = models.User(
            name=user.name,
            email=user.email,
            po_wo_so_number=user.po_wo_so_number,
            site_name=user.site_name,
            company_name=user.company_name,
            mobile_number=user.mobile_number,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = create_access_token(data={"sub": str(new_user.id)})

        return {"message": "User registered successfully", "user_id": new_user.id, "access_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# ✅ Define Login Schema
class LoginRequest(BaseModel):
    email: str
    password: str

# ✅ LOGIN ROUTE (Fixing Password Verification)
@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    
    if not existing_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not pwd_context.verify(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(existing_user.id)})
    return {"access_token": token, "token_type": "bearer"}
    
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
    "Working Days", "Basic", "HRA", "Any Other Allowance", "PF Wages", "Gross",
    "Deductions", "Net Salary", "OT", "Advance Salary", "Bank Transfer Reference",
    "Bonus Detail", "Bonus Paid Date", "Leave Record", "Leave Encashment",
    "Fine Detail", "Damage & Loss Detail"
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
            db_employee = models.EmployeeRecord(
                employee_code=employee["Employee Code"],
                employee_name=employee["Employee Name"],
                uan=employee["UAN"],
                esic_number=employee["ESIC Number"],
                designation=employee["Designation"],
                working_days=employee["Working Days"],
                basic=employee["Basic"],
                hra=employee["HRA"],
                any_other_allowance=employee["Any Other Allowance"],
                pf_wages=employee["PF Wages"],
                gross=employee["Gross"],
                deductions=employee["Deductions"],
                net_salary=employee["Net Salary"],
                ot=employee["OT"],
                advance_salary=employee["Advance Salary"],
                bank_transfer_reference=employee["Bank Transfer Reference"],
                bonus_detail=employee["Bonus Detail"],
                bonus_paid_date=employee["Bonus Paid Date"],
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

# ✅ Print registered routes
@app.on_event("startup")
async def startup_event():
    for route in app.routes:
        print(route.path)

print("FastAPI is running with registered routes:", app.routes)
