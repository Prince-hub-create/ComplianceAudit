from sqlalchemy.orm import Session
from backend.models import Vendor, User, Document
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Create a Vendor
def create_vendor(db: Session, name: str, email: str, phone: str):
    vendor = Vendor(name=name, email=email, phone=phone)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

# ✅ Get All Vendors
def get_vendors(db: Session):
    return db.query(Vendor).all()

# ✅ Get Vendor by ID
def get_vendor(db: Session, vendor_id: int):
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()

# ✅ Delete a Vendor
def delete_vendor(db: Session, vendor_id: int):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor:
        db.delete(vendor)
        db.commit()
    return vendor

# --- ✅ USER AUTHENTICATION LOGIC ---

# ✅ Get user by email (Case-Insensitive Search)
def get_user_by_email(db: Session, email: str):
    print(f"🔍 Debug: Searching user by email - {email}")  # ✅ Debugging log
    user = db.query(User).filter(User.email.ilike(email)).first()  # ✅ Case-insensitive email search
    print(f"🔍 Debug: User found: {user}")  # ✅ Log user data if found
    return user

# ✅ Create a new user (Signup)
def create_user(db: Session, name: str, email: str, po_wo_so_number: str, site_name: str, company_name: str, mobile_number: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(
        name=name,
        email=email,
        po_wo_so_number=po_wo_so_number,
        site_name=site_name,
        company_name=company_name,
        mobile_number=mobile_number,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
