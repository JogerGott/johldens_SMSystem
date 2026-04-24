from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QComboBox, QGridLayout, QDoubleSpinBox)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.payment_repository import PaymentRepository
from src.repositories.invoice_repository import InvoiceRepository
from sqlalchemy import text

class PaymentsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Tesorero Múltiple y Pagos Diarios")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "💰 Movimientos / Historial")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Asentar Nuevo Pago")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(lambda idx: self.load_data() if idx == 0 else self.refresh_invoices_dropdown())

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        btn_refresh = QPushButton("Refrescar Base")
        btn_refresh.setObjectName("ActionBtn")
        btn_refresh.clicked.connect(self.load_data)
        
        bt_layout = QHBoxLayout()
        bt_layout.addStretch()
        bt_layout.addWidget(btn_refresh)
        
        layout.addLayout(bt_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Pago", "Factura Afectada", "Fecha Emisión", "Cantidad Abonada", "Método de Pago"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        self.tab_list.setLayout(layout)
        
        self.load_data()

    def setup_create_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.cb_invoices = QComboBox()
        self.inp_amount = QDoubleSpinBox()
        self.inp_amount.setRange(0.01, 99999.99)
        self.inp_amount.setPrefix("$ ")
        
        self.cb_method = QComboBox()
        self.cb_method.addItems(["Cash", "Transferencia", "Cheque", "Zelle", "POS"])
        
        form_layout.addWidget(QLabel("Factura de Destino:"), 0, 0)
        form_layout.addWidget(self.cb_invoices, 0, 1)
        
        form_layout.addWidget(QLabel("Cuantía a Pagar / Abonar:"), 1, 0)
        form_layout.addWidget(self.inp_amount, 1, 1)
        
        form_layout.addWidget(QLabel("Método / Tipo de Transacción:"), 2, 0)
        form_layout.addWidget(self.cb_method, 2, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Procesar Pago al Balance")
        btn_save.setObjectName("ActionBtn")
        btn_save.setStyleSheet("background-color: #27ae60; padding: 15px; font-size: 14px;")
        btn_save.clicked.connect(self.create_payment_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)
        self.refresh_invoices_dropdown()

    def refresh_invoices_dropdown(self):
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        
        self.cb_invoices.clear()
        
        # Cargar exclusivametne aquellas que tengan una deuda pendiente o saldo parcial
        query = text("SELECT id_invoice, amount, lending_balance FROM invoices WHERE pay_state != 'PAGADO'")
        invoices = session.execute(query).fetchall()
        for i in invoices:
            id_inv = i[0]
            saldo = i[2]
            self.cb_invoices.addItem(f"FAC-{id_inv} (Debe: ${saldo:,.2f})", id_inv)
            
        session.close()

    def load_data(self):
        session = SessionLocal()
        pay_repo = PaymentRepository(session)
        payments = pay_repo.list_all_payments()
        
        self.table.setRowCount(0)
        for row, pay in enumerate(payments):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"PAG-{pay.id_payment}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"FAC-{pay.id_invoice}"))
            self.table.setItem(row, 2, QTableWidgetItem(pay.pay_date.strftime("%Y-%m-%d %H:%M")))
            
            amt_item = QTableWidgetItem(f"${pay.payment_amount:,.2f}")
            amt_item.setForeground(Qt.GlobalColor.darkGreen)
            
            self.table.setItem(row, 3, amt_item)
            self.table.setItem(row, 4, QTableWidgetItem(pay.payment_type.value))
            
        session.close()

    def create_payment_action(self):
        id_invoice = self.cb_invoices.currentData()
        amount = self.inp_amount.value()
        method = self.cb_method.currentText()
        
        if not id_invoice:
            QMessageBox.warning(self, "Error", "Debe seleccionar una factura activa para abonar.")
            return
            
        session = SessionLocal()
        pay_repo = PaymentRepository(session)
        try:
            pay = pay_repo.create_payment(id_invoice, amount, payment_type=method)
            QMessageBox.information(self, "Éxito", f"Pago por ${amount:,.2f} procesado. La factura redujo su balance.")
            
            self.inp_amount.setValue(0)
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error BD", f"Error asegurando el pago:\n\n{e}")
        finally:
            session.close()
