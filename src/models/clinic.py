from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.models.base import Base

class Clinic(Base):
    __tablename__ = "clinics"

    id_clinic = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    telephone = Column(String(20), nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)

    # Relaciones - Una clinica tiene doctores
    doctors = relationship("Doctor", back_populates="clinic")
    # Una clinica también puede estar conectada a pacientes directamente, si así lo indica la regla "PATIENT puede pertenecer a CLINIC"
    patients = relationship("Patient", back_populates="clinic")
