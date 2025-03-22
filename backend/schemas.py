from pydantic import BaseModel, EmailStr


# ✅ Schema for Vendor Creation
class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str


# ✅ Schema for User Signup (Updated & Fixed)
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # ✅ Ensures valid email format
    po_wo_so_number: str
    site_name: str
    company_name: str
    mobile_number: str
    password: str

    class Config:
        from_attributes = True  # ✅ Fix for Pydantic v2 (Replaces orm_mode)


# ✅ Schema for Returning User Data (Fix `orm_mode` for Pydantic v2)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr  # ✅ Ensure email is valid
    po_wo_so_number: str
    site_name: str
    company_name: str
    mobile_number: str

    class Config:
        from_attributes = True  # ✅ Fixes compatibility with FastAPI & Pydantic v2
