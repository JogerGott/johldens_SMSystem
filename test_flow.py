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

        
        box = box_repo.create_box("AZUL", 1)
        
        print("-> Maestros creados con éxito.")

        print(f"\n2. Creando un Job completo asignando la caja {box.id_box}...")
        
        import os
        dummy_pic1 = "teeth_model_sample.jpg"
        dummy_pic2 = "teeth_model_sample2.jpg"

        product_items = [{'id_product': prod_corona.id_product, 'quantity': 1}]
        
        # JOB 1: CON 2 FOTOS
        job1 = job_service.create_full_job(
            id_doctor=doctor.id_doctor, id_patient=patient.id_patient,
            product_items=product_items, id_box=box.id_box, id_clinic=clinic.id_clinic,
            pictures=[dummy_pic1, dummy_pic2]
        )
        print(f"-> Trabajo #{job1.id_job} creado. Adjuntas 2 imágenes.")
        
        # JOB 2: SIN FOTOS
        box2 = box_repo.create_box("ROJA", 2)
        job2 = job_service.create_full_job(
            id_doctor=doctor.id_doctor, id_patient=patient.id_patient,
            product_items=product_items, id_box=box2.id_box, id_clinic=clinic.id_clinic,
            pictures=[]
        )
        print(f"-> Trabajo #{job2.id_job} creado. Adjuntas 0 imágenes.")

        # JOB 3: CON 1 FOTO
        box3 = box_repo.create_box("VERDE", 3)
        job3 = job_service.create_full_job(
            id_doctor=doctor.id_doctor, id_patient=patient.id_patient,
            product_items=product_items, id_box=box3.id_box, id_clinic=clinic.id_clinic,
            pictures=[dummy_pic1]
        )
        print(f"-> Trabajo #{job3.id_job} creado. Adjunta 1 imagen.")

        print(f"\n3. Verificando persistencia de las imágenes localmente...")
        from src.models.job_picture import JobPicture
        pics_job1 = session.query(JobPicture).filter(JobPicture.id_job == job1.id_job).all()
        pics_job2 = session.query(JobPicture).filter(JobPicture.id_job == job2.id_job).all()
        pics_job3 = session.query(JobPicture).filter(JobPicture.id_job == job3.id_job).all()
        
        print(f"Job 1 Pics en BD: {len(pics_job1)} (Ej. Ruta local salvada: {pics_job1[0].file_path if pics_job1 else ''})")
        print(f"Job 2 Pics en BD: {len(pics_job2)}")
        print(f"Job 3 Pics en BD: {len(pics_job3)}")

        assert len(pics_job1) == 2, "El Job 1 debió guardar 2 rutas de imágenes."
        assert len(pics_job2) == 0, "El Job 2 debió guardar 0 rutas de imágenes."
        assert len(pics_job3) == 1, "El Job 3 debió guardar 1 rutas de imágenes."
        assert os.path.exists(pics_job1[0].file_path), "Falla Crítica: La imagen 1 no fue copiada al File System local (assets/job_pictures)"
        assert os.path.exists(pics_job1[1].file_path), "Falla Crítica: La imagen 2 no fue copiada al File System local"
        
        job = job1

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

        print("\n[ÉXITO] TODAS LAS PRUEBAS DE INTEGRACIÓN FUERON SUPERADAS.")
        print("La lógica del negocio opera a la perfección y tu Base de Datos MySQL está respondiendo increíblemente bien.")

    except AssertionError as ae:
        print(f"\n[FALLA] Falla lógica en assert: {ae}")
        session.rollback()
    except Exception as e:
        import traceback
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print(f"\n[ERROR CRÍTICO] Excepción capturada durante el test: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_integration_test()
