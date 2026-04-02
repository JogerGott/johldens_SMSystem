from sqlalchemy.orm import Session
from src.models import Clinic

class ClinicRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_clinic(self, name: str, address: str, telephone: str) -> Clinic:
        new_clinic = Clinic(name=name, address=address, telephone=telephone, active=True)
        self.session.add(new_clinic)
        self.session.commit()
        self.session.refresh(new_clinic)
        return new_clinic

    def check_clinic(self, id_clinic: int) -> Clinic:
        return self.session.query(Clinic).filter(Clinic.id_clinic == id_clinic).first()

    def update_clinic(self, id_clinic: int, update_data: dict) -> Clinic:
        clinic = self.check_clinic(id_clinic)
        if clinic:
            for key, value in update_data.items():
                if hasattr(clinic, key):
                    setattr(clinic, key, value)
            self.session.commit()
            self.session.refresh(clinic)
        return clinic

    def list_clinics(self):
        return self.session.query(Clinic).all()
