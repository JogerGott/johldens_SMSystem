import enum
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum as SqlaEnum, func, DECIMAL
import datetime
from sqlalchemy.orm import relationship
from src.models.base import Base

class PaymentType(enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE = "CHEQUE"
    OTRO = "OTRO"

class Payment(Base):
    __tablename__ = "payments"

    id_payment = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_invoice = Column(Integer, ForeignKey("invoices.id_invoice", ondelete="RESTRICT"), nullable=False)
    
    pay_date = Column(DateTime, nullable=False, server_default=func.now())
    payment_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_type = Column(SqlaEnum(PaymentType), nullable=False, default=PaymentType.EFECTIVO)
    status = Column(Boolean, nullable=False, default=True)

    invoice = relationship("Invoice", back_populates="payments")
