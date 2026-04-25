import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum as SqlaEnum, func, DECIMAL
import datetime
from sqlalchemy.orm import relationship
from src.models.base import Base

class PayState(enum.Enum):
    PAGADO = "PAGADO"
    PARCIAL = "PARCIAL"
    PENDIENTE = "PENDIENTE"

class Invoice(Base):
    __tablename__ = "invoices"

    id_invoice = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # FK Hacia Job
    id_job = Column(Integer, ForeignKey("jobs.id_job", ondelete="RESTRICT"), nullable=False, unique=True)
    
    invoice_date = Column(Date, nullable=True)
    
    amount = Column(DECIMAL(10, 2), nullable=False) 
    lending_balance = Column(DECIMAL(10, 2), nullable=False) 
    
    pay_state = Column(SqlaEnum(PayState), nullable=False, default=PayState.PENDIENTE)

    # Relaciones
    job = relationship("Job")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
