from pydantic import BaseModel, EmailStr

class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str