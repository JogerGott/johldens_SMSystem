from sqlalchemy.orm import Session
from src.models import Patient

class PatientRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_patient(self, id_patient: str, name: str, lastname: str, id_doctor: str, id_clinic: int = None) -> Patient:
        new_patient = Patient(id_patient=id_patient, name=name, last_name=lastname, id_doctor=id_doctor, id_clinic=id_clinic)
        self.session.add(new_patient)
        self.session.commit()
        self.session.refresh(new_patient)
        return new_patient

    def check_patient(self, id_patient: int) -> Patient:
        return self.session.query(Patient).filter(Patient.id_patient == id_patient).first()

    def update_patient_info(self, id_patient: int, update_data: dict) -> Patient:
        patient = self.check_patient(id_patient)
        if patient:
            for key, value in update_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            self.session.commit()
            self.session.refresh(patient)
        return patient

    # No hay fecha de creación en el paciente, pero si tuvieramos un created_at podriamos filtrarlo
    def list_patients_by_month(self, month: int, year: int):
        # Placeholder para futura implementación de registro de fecha si se agrega al SQL Table
        pass
