from sqlalchemy.orm import Session
from src.models import Doctor

class DoctorRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_doctor(self, id_doctor: str, name: str, last_name: str, email: str, telephone: str, id_clinic: int = None) -> Doctor:
        new_doctor = Doctor(
            id_doctor=id_doctor,
            name=name, last_name=last_name, 
            email=email, telephone=telephone, 
            id_clinic=id_clinic, status=True
        )
        self.session.add(new_doctor)
        self.session.commit()
        self.session.refresh(new_doctor)
        return new_doctor

    def check_doctor(self, id_doctor: int) -> Doctor:
        return self.session.query(Doctor).filter(Doctor.id_doctor == id_doctor).first()

    def update_doctor_info(self, id_doctor: int, update_data: dict) -> Doctor:
        doctor = self.check_doctor(id_doctor)
        if doctor:
            for key, value in update_data.items():
                if hasattr(doctor, key):
                    setattr(doctor, key, value)
            self.session.commit()
            self.session.refresh(doctor)
        return doctor

    def list_doctors(self):
        return self.session.query(Doctor).all()

    def list_doctors_by_clinic(self, id_clinic: int):
        return self.session.query(Doctor).filter(Doctor.id_clinic == id_clinic).all()
