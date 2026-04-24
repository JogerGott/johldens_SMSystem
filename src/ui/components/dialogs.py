from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox

class ClinicDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Clínica")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        
        # Titulo
        title = QLabel("Detalles de Clínica")
        title.setObjectName("Subtitle")
        layout.addWidget(title)
        
        # Inputs
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nombre de la clínica")
        
        self.inp_address = QLineEdit()
        self.inp_address.setPlaceholderText("Dirección")
        
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("Teléfono")
        
        layout.addWidget(self.inp_name)
        layout.addWidget(self.inp_address)
        layout.addWidget(self.inp_phone)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar Clínica")
        self.btn_save.setObjectName("ActionBtn")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def get_data(self):
        return {
            "name": self.inp_name.text().strip(),
            "address": self.inp_address.text().strip(),
            "telephone": self.inp_phone.text().strip()
        }

class DoctorDialog(QDialog):
    def __init__(self, clinics_list_tuples, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Doctor")
        self.setFixedSize(380, 420)
        
        layout = QVBoxLayout()
        
        title = QLabel("Detalles del Doctor")
        title.setObjectName("Subtitle")
        layout.addWidget(title)
        
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
        self.cb_clinics.addItem("Ninguna Clínica (Independiente)", None)
        for (id_c, name_c) in clinics_list_tuples:
            self.cb_clinics.addItem(name_c, id_c)
            
        layout.addWidget(self.inp_id)
        layout.addWidget(self.inp_name)
        layout.addWidget(self.inp_lastname)
        layout.addWidget(self.inp_phone)
        layout.addWidget(self.inp_email)
        layout.addWidget(QLabel("Clínica Asistencial Asignada:"))
        layout.addWidget(self.cb_clinics)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar Médico")
        self.btn_save.setObjectName("ActionBtn")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def get_data(self):
        return {
            "id_doctor": self.inp_id.text().strip(),
            "name": self.inp_name.text().strip(),
            "last_name": self.inp_lastname.text().strip(),
            "telephone": self.inp_phone.text().strip(),
            "email": self.inp_email.text().strip(),
            "id_clinic": self.cb_clinics.currentData()
        }
