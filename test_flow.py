import datetime
from src.database.session import SessionLocal, engine
from src.models.base import Base
# Importar repositorios y servicios
from src.repositories.clinic_repository import ClinicRepository
from src.repositories.doctor_repository import DoctorRepository
from src.repositories.patient_repository import PatientRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.box_repository import BoxRepository
from src.services.job_service import JobService
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.payment_repository import PaymentRepository

def run_integration_test():
    print("Iniciando Test de Integración Joldens...")
    
    # Reconstruímos el Schema físico en MySQL para que agarre los últimos cambios como de INT a VARCHAR
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    try:
        # Repos
        clinic_repo = ClinicRepository(session)
        doc_repo = DoctorRepository(session)
        pat_repo = PatientRepository(session)
        prod_repo = ProductRepository(session)
        box_repo = BoxRepository(session)
        inv_repo = InvoiceRepository(session)
        pay_repo = PaymentRepository(session)
        
        job_service = JobService()
        # Sobreescribimos la sesión del servicio para usar la nuestra temporal
        job_service.session = session
        job_service.job_repo.session = session
        job_service.product_repo.session = session
        job_service.box_repo.session = session

        import uuid
        sfx = str(uuid.uuid4())[:8]

        print("\n1. Creando Datos Maestros (Clínica, Doctor, Paciente, Productos y Caja)")
        clinic = clinic_repo.create_clinic("Clínica Joldens " + sfx, "Calle 123", "555-" + sfx)
        doctor = doc_repo.create_doctor("DOC" + sfx, "Juan", "Pérez", f"juan{sfx}@test.com", "111-" + sfx, clinic.id_clinic)
        patient = pat_repo.create_patient("PAT" + sfx, name="Carlos", lastname="Soto", id_doctor=doctor.id_doctor, id_clinic=clinic.id_clinic)
        
        prod_corona = prod_repo.create_product("Corona Cerámica " + sfx, 500, 5) # 5 días
        prod_resina = prod_repo.create_product("Resina Simple " + sfx, 100, 2)   # 2 días

        
        box = box_repo.create_box("Azul", 1)
        
        print("-> Maestros creados con éxito.")

        print(f"\n2. Creando un Job completo asignando la caja {box.id_box}...")
        product_items = [
            {'id_product': prod_corona.id_product, 'quantity': 1},
            {'id_product': prod_resina.id_product, 'quantity': 2}
        ]
        
        job = job_service.create_full_job(
            id_doctor=doctor.id_doctor, id_patient=patient.id_patient,
            product_items=product_items, id_box=box.id_box, id_clinic=clinic.id_clinic
        )
        print(f"-> Trabajo #{job.id_job} creado. Fecha Ingreso: {job.entry_date}. Fecha Entrega: {job.expected_exit_date}")
        assert job.expected_exit_date == datetime.date.today() + datetime.timedelta(days=5), "Error crítico de cálculo de fechas de producción."

        print(f"\n3. Verificando estado de la caja...")
        session.refresh(box)
        print(f"-> Estado de la caja id {box.id_box}: {box.status.value}")
        assert box.status.value == "OCUPADA", "Error: La caja no cambió a OCUPADA."

        print(f"\n4. Generando Factura (Invoice) manual del trabajo por el total (500*1 + 100*2 = 700)...")
        invoice = inv_repo.create_invoice(id_job=job.id_job, amount=700)
        print(f"-> Factura #{invoice.id_invoice} creada. Saldo Pendiente: {invoice.lending_balance}. Estado: {invoice.pay_state.value}")

        print(f"\n5. Realizando un abono (Payment) por la caja de 400...")
        payment = pay_repo.create_payment(id_invoice=invoice.id_invoice, amount=400, payment_type="Efectivo")
        
        session.refresh(invoice)
        print(f"-> Pago #${payment.payment_amount} ejecutado. Nuevo Saldo de Factura: {invoice.lending_balance}. Nuevo Estado: {invoice.pay_state.value}")
        assert invoice.lending_balance == 300, "Error: El abono no descontó correctamente el lending_balance"
        assert invoice.pay_state.value == "PARCIAL", "Error: El estado no cambió a PARCIAL."

        print(f"\n6. Despachando Trabajo (Liberando Caja)...")
        dispatched_job = job_service.dispatch_job(job.id_job)
        session.refresh(box)
        print(f"-> Trabajo #{dispatched_job.id_job} Estado: {dispatched_job.status.value}. Fecha salida: {dispatched_job.exit_date}")
        print(f"-> Nuevo estado de la caja: {box.status.value}")
        assert box.status.value == "LIBRE", "Error: La caja no se liberó tras despachar."

        print("\n[ÉXITO] 🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN FUERON SUPERADAS. 🎉")
        print("La lógica del negocio opera a la perfección y tu Base de Datos MySQL está respondiendo increíblemente bien.")

    except AssertionError as ae:
        print(f"\n[FALLA] Falla lógica en assert: {ae}")
        session.rollback()
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"\n[ERROR CRÍTICO] Excepción capturada durante el test: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_integration_test()
