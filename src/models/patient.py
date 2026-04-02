from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id_patient = Column(String(20), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)

    id_doctor = Column(String(20), ForeignKey("doctors.id_doctor"), nullable=False)
    id_clinic = Column(Integer, ForeignKey("clinics.id_clinic"), nullable=True)
    
    doctor = relationship("Doctor", back_populates="patients")
    clinic = relationship("Clinic", back_populates="patients")
