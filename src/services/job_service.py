import datetime
from src.database.session import SessionLocal
from src.repositories.job_repository import JobRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.box_repository import BoxRepository
from src.models import JobProduct

class JobService:
    def __init__(self):
        self.session = SessionLocal()
        self.job_repo = JobRepository(self.session)
        self.product_repo = ProductRepository(self.session)
        self.box_repo = BoxRepository(self.session)

    # Actualizado ids doctor/patient a tipo str (VARCHAR20)
    def create_full_job(self, id_doctor: str, id_patient: str, product_items: list, id_box: int = None, id_clinic: int = None, pictures: list = []):
        """
        product_items is a list of dicts: [{'id_product': 1, 'quantity': 2}]
        """
        max_time = 0
        products_to_add = []
        
        for p_item in product_items:
            prod = self.product_repo.check_product(p_item['id_product'])
            if prod:
                if prod.production_time > max_time:
                    max_time = prod.production_time
                products_to_add.append({
                    'product': prod,
                    'quantity': p_item['quantity'],
                    'price_historic': prod.price
                })
        
        expected_date = datetime.date.today() + datetime.timedelta(days=max_time)
        
        if id_box:
            box = self.box_repo.check_box(id_box)
            if not box or box.status.value != "LIBRE":
                raise ValueError("La caja seleccionada no esta disponible")
        
        new_job = self.job_repo.create_job(
            id_doctor=id_doctor, id_patient=id_patient, 
            id_box=id_box, id_clinic=id_clinic, expected_exit_date=expected_date
        )
        
        for p in products_to_add:
            jp = JobProduct(
                id_job=new_job.id_job, id_product=p['product'].id_product,
                quantity=p['quantity'], historic_price=p['price_historic']
            )
            self.session.add(jp)
            
        for pic in pictures:
            self.job_repo.add_picture(new_job.id_job, pic)
            
        if id_box:
            self.box_repo.change_box_status(id_box, "OCUPADA")
            
        self.session.commit()
        return new_job
        
    def dispatch_job(self, id_job: int):
        job = self.job_repo.check_job(id_job)
        if job:
            if job.id_box:
                self.box_repo.change_box_status(job.id_box, "LIBRE")
                self.job_repo.release_box(job.id_job)
            self.job_repo.change_job_status(job.id_job, "DESPACHADO")
            job.exit_date = datetime.date.today()
            self.session.commit()
        return job
