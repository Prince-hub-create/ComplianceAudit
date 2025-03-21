from pydantic import BaseModel, EmailStr

# ✅ Schema for Vendor Creation
class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str

# ✅ Schema for User Signup (Updated with Additional Fields)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    po_wo_so_number: str
    site_name: str
    company_name: str
    mobile_number: str
    password: str

# ✅ Schema for Returning User Data
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    po_wo_so_number: str
    site_name: str
    company_name: str
    mobile_number: str

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models
