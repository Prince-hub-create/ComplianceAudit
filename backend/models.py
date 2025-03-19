from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base  # ✅ Correct absolute import
import datetime
from sqlalchemy.sql import func

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    documents = relationship("Document", back_populates="vendor")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    vendor = relationship("Vendor", back_populates="documents")

# Audit Model
class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(255), nullable=False)
    site_name = Column(String(255), nullable=False)
    audit_month = Column(Date, nullable=False)
    status = Column(String(50), default="Pending")
    uploaded_documents = Column(ARRAY(Text))  # Store list of document URLs
    created_at = Column(TIMESTAMP, server_default=func.now())

    observations = relationship("Observation", back_populates="audit")

# Observation Model
class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"))
    comment = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    audit = relationship("Audit", back_populates="observations")

 class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)