from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import Job, JobType, JobStatus, JobPicture, Box, BoxStatus
import datetime

class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_job(self, id_doctor: int, id_patient: int, id_box: int = None, id_clinic: int = None, expected_exit_date=None) -> Job:
        new_job = Job(
            id_doctor=id_doctor, id_patient=id_patient, 
            id_box=id_box, id_clinic=id_clinic,
            entry_date=datetime.date.today(),
            expected_exit_date=expected_exit_date, # Debe ser provisto por un Servicio que sume tiemos de productos
            status=JobStatus.REGISTRADO
        )
        self.session.add(new_job)
        self.session.commit()
        self.session.refresh(new_job)
        return new_job

    def check_job(self, id_job: int) -> Job:
        return self.session.query(Job).filter(Job.id_job == id_job).first()

    def list_job_by_status(self, status: str):
        job_status = JobStatus(status.upper())
        return self.session.query(Job).filter(Job.status == job_status).all()

    def add_picture(self, id_job: int, file_path: str):
        pic = JobPicture(id_job=id_job, file_path=file_path)
        self.session.add(pic)
        self.session.commit()
        return pic

    def list_today_jobs(self):
        today = datetime.date.today()
        return self.session.query(Job).filter(Job.entry_date == today).all()
        
    def jobs_due_today(self):
        today = datetime.date.today()
        return self.session.query(Job).filter(Job.expected_exit_date <= today, Job.status != JobStatus.TERMINADO).all()

    def assign_box(self, id_job: int, id_box: int):
        job = self.check_job(id_job)
        if job:
            job.id_box = id_box
            # Aseguramos que la box pase a ocupada en bd
             # Eso idealmente se llama desde el UseCase/Service, pero aqui se actualiza ref
            self.session.commit()

    def release_box(self, id_job: int):
        job = self.check_job(id_job)
        if job and job.id_box:
            # Quitamos la ref de caja del job
            job.id_box = None
            self.session.commit()

    def change_job_status(self, id_job: int, new_status: str):
        job = self.check_job(id_job)
        if job:
            job.status = JobStatus(new_status.upper())
            self.session.commit()
            self.session.refresh(job)
        return job
