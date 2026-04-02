from sqlalchemy.orm import Session
from src.models import Payment, PaymentType
from src.repositories.invoice_repository import InvoiceRepository
import datetime

class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_payment(self, id_invoice: int, amount: int, payment_type: str) -> Payment:
        ptype = PaymentType(payment_type.upper())
        payment = Payment(
            id_invoice=id_invoice,
            pay_date=datetime.datetime.now(),
            payment_amount=amount,
            payment_type=ptype,
            status=True
        )
        self.session.add(payment)
        self.session.commit()
        
        # Tras descontar, usamos el invoice_repository internamente o 
        # a nivel de BD para asegurarnos de que se reduce la deuda de 'lending_balance'
        inv_repo = InvoiceRepository(self.session)
        inv_repo.add_pay_invoice(id_invoice, amount)
        
        self.session.refresh(payment)
        return payment

    def check_payment(self, id_payment: int) -> Payment:
        return self.session.query(Payment).filter(Payment.id_payment == id_payment).first()

    def list_payments_by_invoice(self, id_invoice: int):
        return self.session.query(Payment).filter(Payment.id_invoice == id_invoice, Payment.status == True).all()

