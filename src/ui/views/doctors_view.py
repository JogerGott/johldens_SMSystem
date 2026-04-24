from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QComboBox, QGridLayout)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.doctor_repository import DoctorRepository
from src.repositories.clinic_repository import ClinicRepository

class DoctorsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top Bar
        title = QLabel("Gestor de Doctores")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "👨‍⚕️ Directorio Médico")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Registrar Doctor")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID (Cédula)", "Nombres", "Apellidos", "Teléfono", "Email", "Clínica", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        btn_refresh = QPushButton("Refrescar Lista")
        btn_refresh.setObjectName("ActionBtn")
        btn_refresh.clicked.connect(self.load_data)
        
        bt_layout = QHBoxLayout()
        bt_layout.addStretch()
        bt_layout.addWidget(btn_refresh)
        
        layout.addLayout(bt_layout)
        layout.addWidget(self.table)
        self.tab_list.setLayout(layout)
        self.load_data()

    def setup_create_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.inp_id = QLineEdit()
        self.inp_id.setPlaceholderText("ID Médico / Cédula")
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nombres")
        self.inp_lastname = QLineEdit()
        self.inp_lastname.setPlaceholderText("Apellidos")
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("Correo Opcional")
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("Teléfono")
        
        self.cb_clinics = QComboBox()
        # Data will be loaded dynamically
        
        form_layout.addWidget(QLabel("Cédula/Indentificación:"), 0, 0)
        form_layout.addWidget(self.inp_id, 0, 1)
        form_layout.addWidget(QLabel("Nombres:"), 1, 0)
        form_layout.addWidget(self.inp_name, 1, 1)
        form_layout.addWidget(QLabel("Apellidos:"), 2, 0)
        form_layout.addWidget(self.inp_lastname, 2, 1)
        form_layout.addWidget(QLabel("Teléfono de Contacto:"), 3, 0)
        form_layout.addWidget(self.inp_phone, 3, 1)
        form_layout.addWidget(QLabel("Correo Electrónico:"), 4, 0)
        form_layout.addWidget(self.inp_email, 4, 1)
        form_layout.addWidget(QLabel("Asociar a Clínica:"), 5, 0)
        form_layout.addWidget(self.cb_clinics, 5, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Guardar Especialista")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_doctor_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)
        self.refresh_clinics_dropdown()

    def load_data(self):
        session = SessionLocal()
        doc_repo = DoctorRepository(session)
        
        doctors = doc_repo.list_doctors()
        
        self.table.setRowCount(0)
        for row, doctor in enumerate(doctors):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(doctor.id_doctor)))
            self.table.setItem(row, 1, QTableWidgetItem(doctor.name))
            self.table.setItem(row, 2, QTableWidgetItem(doctor.last_name))
            self.table.setItem(row, 3, QTableWidgetItem(doctor.telephone or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(doctor.email or "-"))
            
            clinic_name = doctor.clinic.name if doctor.clinic else "Independiente"
            self.table.setItem(row, 5, QTableWidgetItem(clinic_name))
            
            state = "Activo" if doctor.status else "Inactivo"
            self.table.setItem(row, 6, QTableWidgetItem(state))
            
        session.close()

    def on_tab_changed(self, index):
        if index == 1:
            self.refresh_clinics_dropdown()
            
    def refresh_clinics_dropdown(self):
        session = SessionLocal()
        clinic_repo = ClinicRepository(session)
        clinics = clinic_repo.list_clinics()
        
        self.cb_clinics.clear()
        self.cb_clinics.addItem("Ninguna Clínica (Independiente)", None)
        for c in clinics:
            self.cb_clinics.addItem(c.name, c.id_clinic)
            
        session.close()

    def create_doctor_action(self):
        id_doc = self.inp_id.text().strip()
        name = self.inp_name.text().strip()
        lastname = self.inp_lastname.text().strip()
        email = self.inp_email.text().strip()
        phone = self.inp_phone.text().strip()
        id_clinic = self.cb_clinics.currentData()
        
        if not id_doc or not name or not lastname:
            QMessageBox.warning(self, "Error", "El ID, Nombres y Apellidos son obligatorios")
            return
            
        session = SessionLocal()
        doc_repo = DoctorRepository(session)
        try:
            doc_repo.create_doctor(
                id_doctor=id_doc, 
                name=name, 
                last_name=lastname, 
                email=email, 
                telephone=phone, 
                id_clinic=id_clinic
            )
            QMessageBox.information(self, "Éxito", "Doctor registrado correctamente")
            
            self.inp_id.clear()
            self.inp_name.clear()
            self.inp_lastname.clear()
            self.inp_email.clear()
            self.inp_phone.clear()
            
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo guardar el doctor.\n\n{e}")
        finally:
            session.close()
