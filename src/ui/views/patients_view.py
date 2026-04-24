import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QComboBox, QGridLayout)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.patient_repository import PatientRepository
from src.repositories.doctor_repository import DoctorRepository
from src.repositories.clinic_repository import ClinicRepository

class PatientsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titulo Principal
        title = QLabel("Gestor de Pacientes")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Lista / Buscador
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "📋 Directorio de Pacientes")
        
        # Tab 2: Formulario Registro
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Registrar Paciente")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        # Controles Top (Filtros en el futuro, por ahora listado general del mes actual)
        top_controls = QHBoxLayout()
        
        self.cb_month = QComboBox()
        self.cb_month.addItems(["Todos los meses", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        current_month = datetime.date.today().month
        self.cb_month.setCurrentIndex(current_month) # Selecciona mes actual
        
        self.cb_year = QComboBox()
        current_year = datetime.date.today().year
        self.cb_year.addItems([str(current_year - 1), str(current_year), str(current_year + 1)])
        self.cb_year.setCurrentText(str(current_year))
        
        btn_filter = QPushButton("Filtrar")
        btn_filter.setObjectName("ActionBtn")
        btn_filter.clicked.connect(self.load_data)
        
        top_controls.addWidget(QLabel("Mes:"))
        top_controls.addWidget(self.cb_month)
        top_controls.addWidget(QLabel("Año:"))
        top_controls.addWidget(self.cb_year)
        top_controls.addStretch()
        top_controls.addWidget(btn_filter)
        
        layout.addLayout(top_controls)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID (Cédula)", "Nombres", "Apellidos", "Doctor Tratante", "Clínica"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        self.tab_list.setLayout(layout)
        
        self.load_data()

    def setup_create_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Grid para el formulario
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.inp_id = QLineEdit()
        self.inp_name = QLineEdit()
        self.inp_lastname = QLineEdit()
        
        self.cb_doctors = QComboBox()
        self.cb_clinics = QComboBox()
        
        form_layout.addWidget(QLabel("Cédula / Pasaporte:"), 0, 0)
        form_layout.addWidget(self.inp_id, 0, 1)
        
        form_layout.addWidget(QLabel("Nombres:"), 1, 0)
        form_layout.addWidget(self.inp_name, 1, 1)
        
        form_layout.addWidget(QLabel("Apellidos:"), 2, 0)
        form_layout.addWidget(self.inp_lastname, 2, 1)
        
        form_layout.addWidget(QLabel("Clínica Asistencial:"), 3, 0)
        form_layout.addWidget(self.cb_clinics, 3, 1)
        
        form_layout.addWidget(QLabel("Doctor Tratante:"), 4, 0)
        form_layout.addWidget(self.cb_doctors, 4, 1)
        
        self.cb_clinics.currentIndexChanged.connect(self.update_doctors_dropdown)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Registrar Paciente")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_patient_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)

    def load_data(self):
        session = SessionLocal()
        pat_repo = PatientRepository(session)
        doc_repo = DoctorRepository(session)
        clinic_repo = ClinicRepository(session)
        
        # Logica de Filtro
        month_idx = self.cb_month.currentIndex()
        year = int(self.cb_year.currentText())
        
        if month_idx == 0:
            # En vida real tendriamos un pat_repo.list_all_patients()
            # Por ahora simulamos si es 0 (Todos) trae los de enero temporal o requerimos el repo para eso
            patients = pat_repo.list_patients_by_month(datetime.date.today().month, year) # Temporal
        else:
            patients = pat_repo.list_patients_by_month(month_idx, year)
            
        self.table.setRowCount(0)
        for row, patient in enumerate(patients):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(patient.id_patient)))
            self.table.setItem(row, 1, QTableWidgetItem(patient.name))
            self.table.setItem(row, 2, QTableWidgetItem(patient.last_name or "-"))
            
            doc_name = patient.doctor.name + " " + patient.doctor.last_name if patient.doctor else "Desconocido"
            clinic_name = patient.clinic.name if patient.clinic else "Independiente"
            
            self.table.setItem(row, 3, QTableWidgetItem(doc_name))
            self.table.setItem(row, 4, QTableWidgetItem(clinic_name))
            
        session.close()

    def on_tab_changed(self, index):
        # Si entramos a la pestaña de Crear, refrescamos los dropdowns por si se crearon medicos recientes
        if index == 1:
            self.refresh_form_dropdowns()

    def refresh_form_dropdowns(self):
        session = SessionLocal()
        clinic_repo = ClinicRepository(session)
        clinics = clinic_repo.list_clinics()
        
        self.cb_clinics.blockSignals(True)
        self.cb_clinics.clear()
        self.cb_clinics.addItem("Seleccione una Clínica...", None)
        for c in clinics:
            self.cb_clinics.addItem(c.name, c.id_clinic)
        self.cb_clinics.blockSignals(False)
        
        self.update_doctors_dropdown()
        session.close()

    def update_doctors_dropdown(self):
        session = SessionLocal()
        doc_repo = DoctorRepository(session)
        
        id_clinic = self.cb_clinics.currentData()
        if id_clinic:
            doctors = doc_repo.list_doctors_by_clinic(id_clinic)
        else:
            doctors = doc_repo.list_doctors()
            
        self.cb_doctors.clear()
        self.cb_doctors.addItem("Seleccione un Doctor...", None)
        for d in doctors:
            self.cb_doctors.addItem(f"{d.name} {d.last_name}", d.id_doctor)
            
        session.close()

    def create_patient_action(self):
        id_pat = self.inp_id.text().strip()
        name = self.inp_name.text().strip()
        lastname = self.inp_lastname.text().strip()
        id_doc = self.cb_doctors.currentData()
        id_clin = self.cb_clinics.currentData()
        
        if not id_pat or not name or not id_doc:
            QMessageBox.warning(self, "Error", "ID de Paciente, Nombres y un Doctor tratado son campos obligatorios.")
            return
            
        session = SessionLocal()
        pat_repo = PatientRepository(session)
        try:
            pat_repo.create_patient(id_pat, name, lastname, id_doc, id_clin)
            QMessageBox.information(self, "Éxito", "Paciente creado exitosamente.")
            
            # Limpiar
            self.inp_id.clear()
            self.inp_name.clear()
            self.inp_lastname.clear()
            
             # Volver a tab 0 (listado)
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo crear el paciente.\n¿ID duplicado?\n{e}")
        finally:
            session.close()
