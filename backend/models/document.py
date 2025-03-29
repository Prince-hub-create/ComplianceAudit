from sqlalchemy import Column, Integer, String
from backend.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    vendor_id = Column(Integer, nullable=False)  # Assuming it's linked to Vendor
