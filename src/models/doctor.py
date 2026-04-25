from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id_doctor = Column(String(20), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True, unique=True)
    telephone = Column(String(20), nullable=True, unique=True)
    address = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    
    id_clinic = Column(Integer, ForeignKey("clinics.id_clinic", ondelete="SET NULL"), nullable=True)
    
    clinic = relationship("Clinic", back_populates="doctors")
    patients = relationship("Patient", back_populates="doctor")
