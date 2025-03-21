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

# ✅ Ensure backend directory is in the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Import modules
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Function to verify token
def verify_token(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# ✅ Test Route
@app.get("/")
def root():
    return {"message": "Labor Compliance Audit API is running!"}

# ✅ SIGNUP ROUTE (Fixed)
@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # ✅ Hash password
        hashed_password = pwd_context.hash(user.password)

        # ✅ Create new user
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

        # ✅ Generate JWT Token
        token = create_access_token(data={"sub": str(new_user.id)})

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "access_token": token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

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

        return {
            "message": "Files uploaded successfully!",
            "vendor_details": {
                "vendorName": vendorName,
                "vendorAddress": vendorAddress,
                "month": month,
                "principalEmployer": principalEmployer,
                "employerAddress": employerAddress,
                "siteName": siteName,
                "siteAddress": siteAddress,
                "poNumber": poNumber,
                "remarks": remarks
            },
            "files": saved_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")
