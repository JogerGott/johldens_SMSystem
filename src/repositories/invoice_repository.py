from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import Invoice, PayState, Job, Payment
import datetime
from dateutil.relativedelta import relativedelta

class InvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_invoice(self, id_job: int, amount: int) -> Invoice:
        inv = Invoice(
            id_job=id_job,
            invoice_date=datetime.date.today(),
            amount=amount,
            lending_balance=amount,
            pay_state=PayState.PENDIENTE
        )
        self.session.add(inv)
        self.session.commit()
        self.session.refresh(inv)
        return inv

    def check_invoice(self, id_invoice: int) -> Invoice:
        return self.session.query(Invoice).filter(Invoice.id_invoice == id_invoice).first()
        
    def list_all_invoices(self):
        return self.session.query(Invoice).all()

    def list_invoices_by_doctor(self, id_doctor: str):
        return self.session.query(Invoice).join(Job).filter(Job.id_doctor == id_doctor).all()
        
    def list_invoices_by_clinic(self, id_clinic: int):
        return self.session.query(Invoice).join(Job).filter(Job.id_clinic == id_clinic).all()
        
    def list_invoices_by_paystate(self, paystate: str):
        pstate = PayState(paystate.upper())
        return self.session.query(Invoice).filter(Invoice.pay_state == pstate).all()

    def add_pay_invoice(self, id_invoice: int, amount: float):
        """
        Reduce el saldo deudor lending_balance basándose puramente en un monto.
        Se llama despues de verificar un Payment existente o al crear uno.
        """
        import decimal
        inv = self.check_invoice(id_invoice)
        if inv:
            # Convertimos a string primero para evitar problemas de coma flotante y luego a Decimal
            dec_amount = decimal.Decimal(str(amount))
            inv.lending_balance -= dec_amount
            if inv.lending_balance < 0:
                inv.lending_balance = decimal.Decimal('0.00')
            self.session.commit()
            self.update_paystate(id_invoice)

    def lending_balance_by_doctor(self, id_doctor: str):
        result = self.session.query(func.sum(Invoice.lending_balance)).join(Job).filter(Job.id_doctor == id_doctor).scalar()
        return result or 0

    def lending_balance_by_clinic(self, id_clinic: int):
        result = self.session.query(func.sum(Invoice.lending_balance)).join(Job).filter(Job.id_clinic == id_clinic).scalar()
        return result or 0

    def total_invoices_last_month_by_doctor(self, id_doctor: str):
        last_month = datetime.date.today() - relativedelta(months=1)
        start_date = last_month.replace(day=1)
        # End of last month by adding 1 month to start and subtracting 1 day
        end_date = start_date + relativedelta(months=1, days=-1)
        return self.session.query(Invoice).join(Job).filter(
            Job.id_doctor == id_doctor, 
            Invoice.invoice_date >= start_date, 
            Invoice.invoice_date <= end_date
        ).count()

    def total_invoices_last_month_by_clinic(self, id_clinic: int):
        last_month = datetime.date.today() - relativedelta(months=1)
        start_date = last_month.replace(day=1)
        end_date = start_date + relativedelta(months=1, days=-1)
        return self.session.query(Invoice).join(Job).filter(
            Job.id_clinic == id_clinic, 
            Invoice.invoice_date >= start_date, 
            Invoice.invoice_date <= end_date
        ).count()

    def total_billed_by_doctor(self, id_doctor: str):
        result = self.session.query(func.sum(Invoice.amount)).join(Job).filter(Job.id_doctor == id_doctor).scalar()
        return result or 0

    def total_billed_by_clinic(self, id_clinic: int):
        result = self.session.query(func.sum(Invoice.amount)).join(Job).filter(Job.id_clinic == id_clinic).scalar()
        return result or 0

    def update_paystate(self, id_invoice: int):
        inv = self.check_invoice(id_invoice)
        if not inv: return

        if inv.lending_balance == 0:
            inv.pay_state = PayState.PAGADO
        elif inv.lending_balance < inv.amount:
            inv.pay_state = PayState.PARCIAL
        else:
            inv.pay_state = PayState.PENDIENTE
            
        self.session.commit()
        self.session.refresh(inv)

    def check_existence_invoice_for_job(self, id_job: int) -> bool:
        inv = self.session.query(Invoice).filter(Invoice.id_job == id_job).first()
        return inv is not None
