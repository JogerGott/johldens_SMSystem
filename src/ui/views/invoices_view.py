from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QComboBox, QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.job_repository import JobRepository
from src.repositories.doctor_repository import DoctorRepository
from sqlalchemy import text

class InvoicesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Gestor de Facturación Cuentas por Cobrar")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "💳 Archivo Histórico de Facturas")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "🧾 Generar Factura Manual")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(lambda idx: self.load_data() if idx == 0 else self.refresh_jobs_dropdown())

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        top_controls = QHBoxLayout()
        
        self.cb_filter_state = QComboBox()
        self.cb_filter_state.addItems(["Todas", "Pendiente", "Parcial", "Pagado"])
        
        self.cb_filter_doctor = QComboBox()
        self.cb_filter_doctor.addItem("Todos los Doctores", None)
        
        btn_filter = QPushButton("Aplicar Filtros")
        btn_filter.setObjectName("ActionBtn")
        btn_filter.clicked.connect(self.load_data)
        
        top_controls.addWidget(QLabel("Estado:"))
        top_controls.addWidget(self.cb_filter_state)
        top_controls.addWidget(QLabel("Doctor:"))
        top_controls.addWidget(self.cb_filter_doctor)
        top_controls.addStretch()
        top_controls.addWidget(btn_filter)
        
        layout.addLayout(top_controls)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Factura #", "Orden Trabajo", "Fecha", "Monto Total", "Saldo Deudor", "Estado", "Clínica/Doctor"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Resumen Rápido (Footer)
        self.lbl_summary = QLabel("Total Deuda Acumulada: $0.00")
        self.lbl_summary.setObjectName("Subtitle")
        self.lbl_summary.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(self.lbl_summary)
        
        self.tab_list.setLayout(layout)
        
        self.refresh_doctor_dropdown_filter()
        self.load_data()

    def setup_create_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.cb_jobs = QComboBox()
        self.inp_amount = QDoubleSpinBox()
        self.inp_amount.setRange(0.01, 99999.99)
        self.inp_amount.setPrefix("$ ")
        
        form_layout.addWidget(QLabel("Trabajo/Orden (Sin Facturar):"), 0, 0)
        form_layout.addWidget(self.cb_jobs, 0, 1)
        
        form_layout.addWidget(QLabel("Monto de Factura:"), 1, 0)
        form_layout.addWidget(self.inp_amount, 1, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Emitir Factura a Cuenta")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_invoice_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)

    def refresh_doctor_dropdown_filter(self):
        session = SessionLocal()
        doc_repo = DoctorRepository(session)
        for doc in doc_repo.list_doctors():
            self.cb_filter_doctor.addItem(f"{doc.name} {doc.last_name}", doc.id_doctor)
        session.close()

    def refresh_jobs_dropdown(self):
        session = SessionLocal()
        job_repo = JobRepository(session)
        inv_repo = InvoiceRepository(session)
        
        self.cb_jobs.clear()
        
        # Load only jobs that do NOT have an invoice assigned yet.
        # Temporarily iterating through today's jobs or some status
        query = text("SELECT id_job, entry_date FROM jobs")
        all_jobs = session.execute(query).fetchall()
        for j in all_jobs:
            id_job = j[0]
            if not inv_repo.check_existence_invoice_for_job(id_job):
                self.cb_jobs.addItem(f"Orden #ORD-{id_job} ({j[1]})", id_job)
                
        session.close()

    def load_data(self):
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        
        estado = self.cb_filter_state.currentText()
        doc = self.cb_filter_doctor.currentData()
        
        # Filtro hibrido ultra rapido iterando post-db (para MVP)
        if doc:
            invoices_raw = inv_repo.list_invoices_by_doctor(doc)
        elif estado != "Todas":
            invoices_raw = inv_repo.list_invoices_by_paystate(estado.upper())
        else:
            invoices_raw = inv_repo.list_all_invoices()
            
        # Post-filter si hay multiples (MVP constraint bypass)
        final_invoices = []
        total_balance = 0.0
        
        for inv in invoices_raw:
            if estado != "Todas" and inv.pay_state.value != estado.upper(): continue
            if doc and inv.job and inv.job.id_doctor != doc: continue
            
            final_invoices.append(inv)
            total_balance += float(inv.lending_balance)
            
        self.table.setRowCount(0)
        for row, inv in enumerate(final_invoices):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"FAC-{inv.id_invoice}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"ORD-{inv.id_job}"))
            self.table.setItem(row, 2, QTableWidgetItem(inv.invoice_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 3, QTableWidgetItem(f"${inv.amount:,.2f}"))
            
            bal_item = QTableWidgetItem(f"${inv.lending_balance:,.2f}")
            if inv.lending_balance > 0: bal_item.setForeground(Qt.GlobalColor.darkRed)
            
            self.table.setItem(row, 4, bal_item)
            
            estado_inv = inv.pay_state.value
            itm_est = QTableWidgetItem(estado_inv)
            if estado_inv == "PAGADO": itm_est.setForeground(Qt.GlobalColor.darkGreen)
            
            self.table.setItem(row, 5, itm_est)
            
            if inv.job:
                doc_name = inv.job.doctor.last_name if inv.job.doctor else "-"
                clin_name = inv.job.clinic.name if inv.job.clinic else "Indep."
                self.table.setItem(row, 6, QTableWidgetItem(f"{clin_name} / Dr. {doc_name}"))
            else:
                self.table.setItem(row, 6, QTableWidgetItem("-"))
                
        self.lbl_summary.setText(f"Total Deuda Mostrada: ${total_balance:,.2f}")
        session.close()

    def create_invoice_action(self):
        id_job = self.cb_jobs.currentData()
        amount = self.inp_amount.value()
        
        if not id_job:
            QMessageBox.warning(self, "Error", "No hay trabajos seleccionados para facturar.")
            return
            
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        try:
            # Check existance first (Concurrency)
            if inv_repo.check_existence_invoice_for_job(id_job):
                QMessageBox.critical(self, "Conflicto", "Esta orden ya se encuentra facturada.")
                return
                
            inv = inv_repo.create_invoice(id_job, amount)
            QMessageBox.information(self, "Éxito", f"Factura FAC-{inv.id_invoice} emitida por $ {amount}")
            
            self.inp_amount.setValue(0)
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Fallo al emitir la factura:\n{e}")
        finally:
            session.close()
