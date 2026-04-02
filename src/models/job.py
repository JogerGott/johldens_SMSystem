import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SqlaEnum
from sqlalchemy.orm import relationship
from src.models.base import Base

class JobType(enum.Enum):
    NUEVO = "NUEVO"
    REPETICION = "REPETICION"
    GARANTIA = "GARANTIA"

class JobStatus(enum.Enum):
    REGISTRADO = "REGISTRADO"
    EN_PROCESO = "EN_PROCESO"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    TERMINADO = "TERMINADO"
    FACTURADO = "FACTURADO"
    DESPACHADO = "DESPACHADO"

class Job(Base):
    __tablename__ = "jobs"

    id_job = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_type = Column(SqlaEnum(JobType), nullable=False, default=JobType.NUEVO)
    description = Column(String(300), nullable=True)
    
    entry_date = Column(Date, nullable=False)
    expected_exit_date = Column(Date, nullable=False)
    exit_date = Column(Date, nullable=True)
    status = Column(SqlaEnum(JobStatus), nullable=False, default=JobStatus.REGISTRADO)

    id_doctor = Column(String(20), ForeignKey("doctors.id_doctor"), nullable=False) # Actualizado
    id_patient = Column(String(20), ForeignKey("patients.id_patient"), nullable=False) # Actualizado
    id_box = Column(Integer, ForeignKey("boxes.id_box"), nullable=True)
    id_clinic = Column(Integer, ForeignKey("clinics.id_clinic"), nullable=True)

    doctor = relationship("Doctor")
    patient = relationship("Patient")
    box = relationship("Box")
    clinic = relationship("Clinic")

    products = relationship("JobProduct", back_populates="job", cascade="all, delete-orphan")
    pictures = relationship("JobPicture", back_populates="job", cascade="all, delete-orphan")
