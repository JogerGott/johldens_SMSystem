import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SqlaEnum, func
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
    id_job = Column(Integer, ForeignKey("jobs.id_job"), nullable=False, unique=True)
    
    invoice_date = Column(Date, nullable=False, default=datetime.date.today)
    detail = Column(String(300), nullable=True)
    
    amount = Column(Integer, nullable=False) 
    lending_balance = Column(Integer, nullable=False) 
    
    pay_state = Column(SqlaEnum(PayState), nullable=False, default=PayState.PENDIENTE)

    # Relaciones
    job = relationship("Job")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
