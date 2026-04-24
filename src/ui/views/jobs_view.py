from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QComboBox, QGridLayout, QListWidget, QSpinBox,
                             QFileDialog)
from PyQt6.QtCore import Qt
import datetime

from src.database.session import SessionLocal
from src.repositories.job_repository import JobRepository
from src.repositories.patient_repository import PatientRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.box_repository import BoxRepository
from src.services.job_service import JobService

class JobsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Monitor de Trabajos de Laboratorio")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "📋 Trabajos Activos")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Ingresar Trabajo")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        top_controls = QHBoxLayout()
        self.cb_status_filter = QComboBox()
        self.cb_status_filter.addItems(["Todos (Pendientes)", "Registrado", "En_Proceso", "Despachado", "Terminado"])
        
        btn_filter = QPushButton("Filtrar / Refrescar")
        btn_filter.setObjectName("ActionBtn")
        btn_filter.clicked.connect(self.load_data)
        
        top_controls.addWidget(QLabel("Estado:"))
        top_controls.addWidget(self.cb_status_filter)
        top_controls.addStretch()
        top_controls.addWidget(btn_filter)
        
        layout.addLayout(top_controls)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["No. Orden", "Ingreso", "Vencimiento", "Doctor", "Paciente", "Caja", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Despachar Button
        self.btn_dispatch = QPushButton("Despachar Trabajo Seleccionado (Liberar Caja)")
        self.btn_dispatch.setObjectName("DangerBtn")
        self.btn_dispatch.setStyleSheet("background-color: #f39c12;") # Naranja
        self.btn_dispatch.clicked.connect(self.dispatch_selected_job)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_dispatch)
        layout.addLayout(bottom_layout)
        
        self.tab_list.setLayout(layout)
        self.load_data()

    def setup_create_tab(self):
        self.cart_items = [] # list of dictionaries {'id_product': int, 'name': str, 'quantity': int}
        self.picture_paths = []
        
        layout = QHBoxLayout() # Left side: Forms, Right side: Cart & Submit
        
        # --- LEFT SIDE ---
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.cb_patient = QComboBox()
        self.cb_box = QComboBox()
        
        form_layout.addWidget(QLabel("Paciente Asociado:"), 0, 0)
        form_layout.addWidget(self.cb_patient, 0, 1)
        
        form_layout.addWidget(QLabel("Asignar Caja (Física):"), 1, 0)
        form_layout.addWidget(self.cb_box, 1, 1)
        
        self.btn_attach = QPushButton("📸 Adjuntar Fotos del Molde/Trabajo")
        self.btn_attach.clicked.connect(self.attach_pictures)
        self.lbl_pictures = QLabel("0 fotos adjuntadas.")
        
        form_layout.addWidget(self.btn_attach, 2, 0)
        form_layout.addWidget(self.lbl_pictures, 2, 1)
        
        left_panel.addLayout(form_layout)
        
        # Add Product Section
        left_panel.addWidget(QLabel("\nAñadir Tratamientos / Prótesis:"))
        add_prod_layout = QHBoxLayout()
        self.cb_product = QComboBox()
        self.inp_qty = QSpinBox()
        self.inp_qty.setRange(1, 100)
        btn_add_cart = QPushButton("+ Agregar")
        btn_add_cart.setObjectName("ActionBtn")
        btn_add_cart.clicked.connect(self.add_to_cart)
        
        add_prod_layout.addWidget(self.cb_product, stretch=1)
        add_prod_layout.addWidget(QLabel("Cant:"))
        add_prod_layout.addWidget(self.inp_qty)
        add_prod_layout.addWidget(btn_add_cart)
        left_panel.addLayout(add_prod_layout)
        
        # --- RIGHT SIDE ---
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Resumen del Trabajo (Carrito):"))
        self.list_cart = QListWidget()
        right_panel.addWidget(self.list_cart)
        
        btn_clear = QPushButton("Vaciar Carrito")
        btn_clear.clicked.connect(self.clear_cart)
        right_panel.addWidget(btn_clear)
        
        btn_submit = QPushButton("Procesar Orden (Crear Job)")
        btn_submit.setObjectName("ActionBtn")
        btn_submit.setStyleSheet("background-color: #27ae60; padding: 15px; font-size: 14px;")
        btn_submit.clicked.connect(self.submit_job)
        right_panel.addWidget(btn_submit)
        
        layout.addLayout(left_panel, stretch=6)
        layout.addSpacing(20)
        layout.addLayout(right_panel, stretch=4)
        
        self.tab_create.setLayout(layout)

    def load_data(self):
        session = SessionLocal()
        job_repo = JobRepository(session)
        
        status = self.cb_status_filter.currentText()
        if status == "Todos (Pendientes)":
            jobs = job_repo.jobs_due_today() # Temporarily using this to show pending, normally we'd pull all non-terminated
        else:
            jobs = job_repo.list_job_by_status(status.upper())
            
        self.table.setRowCount(0)
        for row, job in enumerate(jobs):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"ORD-{job.id_job}"))
            self.table.setItem(row, 1, QTableWidgetItem(job.entry_date.strftime("%Y-%m-%d")))
            
            due_item = QTableWidgetItem(job.expected_exit_date.strftime("%Y-%m-%d"))
            if job.expected_exit_date < datetime.date.today() and job.status.value != "TERMINADO":
                due_item.setForeground(Qt.GlobalColor.darkRed) # Overdue
            
            self.table.setItem(row, 2, due_item)
            
            doc_name = job.doctor.name if job.doctor else "N/A"
            pat_name = job.patient.name if job.patient else "N/A"
            box_info = str(job.id_box) if job.id_box else "Sin Caja"
            
            self.table.setItem(row, 3, QTableWidgetItem(doc_name))
            self.table.setItem(row, 4, QTableWidgetItem(pat_name))
            self.table.setItem(row, 5, QTableWidgetItem(box_info))
            self.table.setItem(row, 6, QTableWidgetItem(job.status.value))
            
        session.close()

    def on_tab_changed(self, index):
        if index == 1:
            self.refresh_dropdowns()

    def refresh_dropdowns(self):
        session = SessionLocal()
        
        # Patients
        pat_repo = PatientRepository(session)
        self.cb_patient.clear()
        self.cb_patient.addItem("Seleccione un Paciente...", None)
        for p in pat_repo.list_patients_by_month(datetime.date.today().month, datetime.date.today().year): # Should be all patients
             self.cb_patient.addItem(f"{p.id_patient} | {p.name} {p.last_name}", p) # Storing object
        
        # Boxes
        box_repo = BoxRepository(session)
        self.cb_box.clear()
        self.cb_box.addItem("Sin Caja (Archivado)", None)
        for b in box_repo.list_available_box():
             self.cb_box.addItem(f"Caja {b.color.value.capitalize()} #{b.number}", b.id_box)
             
        # Products
        prod_repo = ProductRepository(session)
        self.cb_product.clear()
        for pr in prod_repo.list_active_products():
             self.cb_product.addItem(f"{pr.name} (${pr.price})", {"id_product": pr.id_product, "name": pr.name})
             
        session.close()

    def add_to_cart(self):
        prod_data = self.cb_product.currentData()
        if not prod_data: return
        qty = self.inp_qty.value()
        
        self.cart_items.append({'id_product': prod_data["id_product"], 'name': prod_data["name"], 'quantity': qty})
        self.list_cart.addItem(f"{qty}x {prod_data['name']}")
        self.inp_qty.setValue(1)

    def attach_pictures(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Imágenes del Molde", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if files:
            self.picture_paths.extend(files)
            self.lbl_pictures.setText(f"{len(self.picture_paths)} fotos listas para adjuntar.")

    def clear_cart(self):
        self.cart_items = []
        self.picture_paths = []
        self.list_cart.clear()
        self.lbl_pictures.setText("0 fotos adjuntadas.")

    def submit_job(self):
        patient_obj = self.cb_patient.currentData()
        id_box = self.cb_box.currentData()
        
        if not patient_obj:
            QMessageBox.warning(self, "Error", "Debe seleccionar el paciente que solicita el trabajo.")
            return
            
        if not self.cart_items:
            QMessageBox.warning(self, "Error", "Debe añadir tratamientos al carrito.")
            return
            
        try:
            job_serv = JobService()
            job = job_serv.create_full_job(
                id_doctor=patient_obj.id_doctor, 
                id_patient=patient_obj.id_patient,
                product_items=self.cart_items,
                id_box=id_box,
                id_clinic=patient_obj.id_clinic,
                pictures=self.picture_paths
            )
            QMessageBox.information(self, "Orden Creada", f"Orden #ORD-{job.id_job} registrada en sistema.\nFecha de Entrega: {job.expected_exit_date.strftime('%Y-%m-%d')}")
            self.clear_cart()
            self.tabs.setCurrentIndex(0)
            self.load_data()
            
        except Exception as e:
             QMessageBox.critical(self, "Error de Sistema", f"No se pudo procesar la orden:\n\n{e}")

    def dispatch_selected_job(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione una orden de la lista para despachar.")
            return
            
        # Get Job ID from first col (Eg: ORD-14)
        order_str = self.table.item(selected, 0).text()
        id_job = int(order_str.replace("ORD-", ""))
        
        reply = QMessageBox.question(self, 'Despachar', f'¿Seguro que desea marcar la orden {order_str} como despachada? (Esto liberará su caja)',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            job_serv = JobService()
            job_serv.dispatch_job(id_job)
            QMessageBox.information(self, "Éxito", f"Orden {order_str} despachada con éxito.")
            self.load_data()
