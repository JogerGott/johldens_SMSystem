from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.clinic_repository import ClinicRepository

class ClinicsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top Bar
        title = QLabel("Gestor de Clínicas")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "🏥 Listado de Clínicas")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Registrar Clínica")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.tabs.currentChanged.connect(lambda idx: self.load_data() if idx == 0 else None)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Dirección", "Teléfono", "Estado"])
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
        
        # Cargar Data Inicial
        self.load_data()
        
    def setup_create_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.inp_name = QLineEdit()
        self.inp_address = QLineEdit()
        self.inp_phone = QLineEdit()
        
        form_layout.addWidget(QLabel("Nombre de la clínica:"), 0, 0)
        form_layout.addWidget(self.inp_name, 0, 1)
        form_layout.addWidget(QLabel("Dirección:"), 1, 0)
        form_layout.addWidget(self.inp_address, 1, 1)
        form_layout.addWidget(QLabel("Teléfono de Contacto:"), 2, 0)
        form_layout.addWidget(self.inp_phone, 2, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Guardar Clínica")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_clinic_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)

    def load_data(self):
        session = SessionLocal()
        repo = ClinicRepository(session)
        clinics = repo.list_clinics()
        
        self.table.setRowCount(0)
        for row, clinic in enumerate(clinics):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(clinic.id_clinic)))
            self.table.setItem(row, 1, QTableWidgetItem(clinic.name))
            self.table.setItem(row, 2, QTableWidgetItem(clinic.address))
            self.table.setItem(row, 3, QTableWidgetItem(clinic.telephone))
            state = "Activa" if clinic.active else "Inactiva"
            self.table.setItem(row, 4, QTableWidgetItem(state))
            
        session.close()

    def create_clinic_action(self):
        name = self.inp_name.text().strip()
        address = self.inp_address.text().strip()
        phone = self.inp_phone.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Error", "El nombre y el teléfono son obligatorios")
            return
            
        session = SessionLocal()
        repo = ClinicRepository(session)
        try:
            repo.create_clinic(name, address, phone)
            QMessageBox.information(self, "Éxito", "Clínica registrada correctamente")
            
            self.inp_name.clear()
            self.inp_address.clear()
            self.inp_phone.clear()
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo guardar la clínica. ¿Nombre/Tel duplicado?\n\n{e}")
        finally:
            session.close()
