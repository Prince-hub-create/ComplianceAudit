from sqlalchemy import Column, Integer, String
from backend.database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)

