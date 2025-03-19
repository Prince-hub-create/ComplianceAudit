import sys
import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext  # For password hashing

# Ensure the backend directory is in the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from backend.database import SessionLocal
from backend import crud, models
from backend.schemas import VendorCreate, UserCreate  # ✅ Import schemas

app = FastAPI()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test Route
@app.get("/")
def root():
    return {"message": "Labor Compliance Audit API is running!"}

# Get All Vendors
@app.get("/vendors/")
def read_vendors(db: Session = Depends(get_db)):
    vendors = db.query(models.Vendor).all()
    if not vendors:
        raise HTTPException(status_code=404, detail="No vendors found")
    return vendors

# Add Vendor
@app.post("/vendors/")
def add_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_vendor(db, vendor.name, vendor.email, vendor.phone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vendor: {str(e)}")

# ✅ **User Registration Route**
@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user(db, user.name, user.email, user.password)
    return {"message": "User registered successfully", "user_id": new_user.id}
