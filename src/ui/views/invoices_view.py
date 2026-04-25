from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QComboBox, QGridLayout, QDoubleSpinBox,
                             QLineEdit, QListWidget, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter

from src.database.session import SessionLocal
from src.repositories.invoice_repository import InvoiceRepository
from src.repositories.job_repository import JobRepository
from src.repositories.doctor_repository import DoctorRepository
from src.repositories.payment_repository import PaymentRepository
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
        
        self.tab_search = QWidget()
        self.setup_search_tab()
        self.tabs.addTab(self.tab_search, "🔍 Detalle de Factura")
        
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
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
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
        
        self.cb_jobs.currentIndexChanged.connect(self.calculate_invoice_amount)
        
        form_layout.addWidget(QLabel("Monto de Factura (Auto-calculado):"), 1, 0)
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

    def setup_search_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        search_layout = QHBoxLayout()
        self.inp_inv_search = QLineEdit()
        self.inp_inv_search.setPlaceholderText("Buscar por # Factura (ej: 12)...")
        btn_search = QPushButton("Buscar")
        btn_search.setObjectName("ActionBtn")
        btn_search.clicked.connect(self.perform_invoice_search)
        
        search_layout.addWidget(self.inp_inv_search)
        search_layout.addWidget(btn_search)
        
        layout.addLayout(search_layout)
        
        self.cb_search_results = QComboBox()
        self.cb_search_results.currentIndexChanged.connect(self.display_searched_invoice)
        layout.addWidget(QLabel("Resultados de Búsqueda:"))
        layout.addWidget(self.cb_search_results)
        
        self.inv_detail_widget = QWidget()
        detail_layout = QGridLayout()
        
        self.lbl_det_factura = QLabel("-")
        self.lbl_det_estado = QLabel("-")
        self.lbl_det_monto = QLabel("-")
        self.lbl_det_saldo = QLabel("-")
        self.lbl_det_clinic = QLabel("-")
        
        self.list_products = QListWidget()
        self.list_payments = QListWidget()
        
        detail_layout.addWidget(QLabel("<b>Factura No:</b>"), 0, 0)
        detail_layout.addWidget(self.lbl_det_factura, 0, 1)
        detail_layout.addWidget(QLabel("<b>Estado:</b>"), 0, 2)
        detail_layout.addWidget(self.lbl_det_estado, 0, 3)
        
        detail_layout.addWidget(QLabel("<b>Monto Total:</b>"), 1, 0)
        detail_layout.addWidget(self.lbl_det_monto, 1, 1)
        detail_layout.addWidget(QLabel("<b>Saldo Deudor:</b>"), 1, 2)
        detail_layout.addWidget(self.lbl_det_saldo, 1, 3)
        
        detail_layout.addWidget(QLabel("<b>Doctor/Clínica:</b>"), 2, 0)
        detail_layout.addWidget(self.lbl_det_clinic, 2, 1, 1, 3)
        
        detail_layout.addWidget(QLabel("<b>Tratamientos Cobrados:</b>"), 3, 0, 1, 2)
        detail_layout.addWidget(self.list_products, 4, 0, 1, 2)
        
        detail_layout.addWidget(QLabel("<b>Historial de Pagos:</b>"), 3, 2, 1, 2)
        detail_layout.addWidget(self.list_payments, 4, 2, 1, 2)
        
        self.btn_pdf = QPushButton("Generar PDF de Factura")
        self.btn_pdf.setObjectName("ActionBtn")
        self.btn_pdf.setStyleSheet("background-color: #27ae60; color: white;")
        self.btn_pdf.clicked.connect(self.generate_invoice_pdf)
        
        detail_layout.addWidget(self.btn_pdf, 5, 0, 1, 4)
        
        self.inv_detail_widget.setLayout(detail_layout)
        self.inv_detail_widget.setVisible(False)
        
        layout.addWidget(self.inv_detail_widget)
        self.tab_search.setLayout(layout)

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
        # Forzar el cálculo para el primer elemento que se carga por defecto si lo hay
        self.calculate_invoice_amount()

    def calculate_invoice_amount(self):
        id_job = self.cb_jobs.currentData()
        if not id_job:
            self.inp_amount.setValue(0.0)
            return
            
        session = SessionLocal()
        job_repo = JobRepository(session)
        job = job_repo.check_job(id_job)
        if job:
            total = sum([float(p.historic_price) * p.quantity for p in job.products])
            self.inp_amount.setValue(total)
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

    def perform_invoice_search(self):
        query = self.inp_inv_search.text().lower()
        if not query: return
        
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        all_invoices = inv_repo.list_all_invoices()
        
        self.cb_search_results.blockSignals(True)
        self.cb_search_results.clear()
        self.cb_search_results.addItem("Seleccione un resultado...", None)
        
        for inv in all_invoices:
            if query in str(inv.id_invoice) or query in str(inv.id_job):
                self.cb_search_results.addItem(f"FAC-{inv.id_invoice} | ORD-{inv.id_job} | {inv.pay_state.value}", inv.id_invoice)
                
        self.cb_search_results.blockSignals(False)
        self.inv_detail_widget.setVisible(False)
        session.close()

    def display_searched_invoice(self):
        id_inv = self.cb_search_results.currentData()
        if not id_inv:
            self.inv_detail_widget.setVisible(False)
            return
            
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        pay_repo = PaymentRepository(session)
        
        inv = inv_repo.check_invoice(id_inv)
        if inv:
            self.lbl_det_factura.setText(f"FAC-{inv.id_invoice} (Fecha: {inv.invoice_date})")
            self.lbl_det_estado.setText(inv.pay_state.value)
            self.lbl_det_monto.setText(f"${inv.amount:,.2f}")
            self.lbl_det_saldo.setText(f"${inv.lending_balance:,.2f}")
            
            if inv.job:
                doc_name = f"{inv.job.doctor.name} {inv.job.doctor.last_name}" if inv.job.doctor else "N/A"
                clin_name = inv.job.clinic.name if inv.job.clinic else "N/A"
                self.lbl_det_clinic.setText(f"Cli: {clin_name} / Dr: {doc_name} (ORD-{inv.job.id_job})")
            else:
                self.lbl_det_clinic.setText("-")
                
            self.list_products.clear()
            if inv.job:
                for prod in inv.job.products:
                    subtotal = prod.quantity * prod.historic_price
                    prod_name = prod.product.name if prod.product else "Desconocido"
                    self.list_products.addItem(f"{prod.quantity}x {prod_name} (ID:{prod.id_product}) - $ {subtotal:,.2f}")
            
            self.list_payments.clear()
            payments = pay_repo.list_payments_by_invoice(inv.id_invoice)
            for pay in payments:
                date_str = pay.pay_date.strftime("%Y-%m-%d %H:%M")
                self.list_payments.addItem(f"[{date_str}] {pay.payment_type.value}: $ {pay.payment_amount:,.2f}")
                
            self.inv_detail_widget.setVisible(True)
            
        session.close()

    def generate_invoice_pdf(self):
        id_inv = self.cb_search_results.currentData()
        if not id_inv: return
        
        import os
        
        # Crear directorio automático
        folder_path = os.path.abspath(os.path.join("assets", "Invoices_pdf", str(id_inv)))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        file_path = os.path.join(folder_path, f"Factura_FAC-{id_inv}.pdf")
        
        session = SessionLocal()
        inv_repo = InvoiceRepository(session)
        pay_repo = PaymentRepository(session)
        inv = inv_repo.check_invoice(id_inv)
        if not inv:
            session.close()
            return
            
        payments = pay_repo.list_payments_by_invoice(id_inv)
        
        doc_name = f"{inv.job.doctor.name} {inv.job.doctor.last_name}" if inv.job and inv.job.doctor else "N/A"
        clin_name = inv.job.clinic.name if inv.job and inv.job.clinic else "N/A"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 0; padding: 20px; }}
                .header {{ border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
                .header table {{ width: 100%; }}
                .header h1 {{ margin: 0; color: #2c3e50; font-size: 28px; letter-spacing: 1px; text-transform: uppercase; }}
                .header h3 {{ margin: 5px 0 0 0; color: #7f8c8d; font-size: 14px; font-weight: normal; }}
                .invoice-title {{ text-align: right; }}
                .invoice-title h2 {{ margin: 0; color: #34495e; font-size: 24px; }}
                .invoice-title p {{ margin: 5px 0 0 0; font-size: 14px; color: #7f8c8d; }}
                
                .info-section {{ width: 100%; margin-bottom: 30px; }}
                .info-section td {{ vertical-align: top; width: 50%; }}
                .box {{ border: 1px solid #ecf0f1; background-color: #fcfcfc; padding: 15px; border-radius: 4px; }}
                .box h4 {{ margin-top: 0; color: #2980b9; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; }}
                
                table.data {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 13px; }}
                table.data th {{ background-color: #2c3e50; color: white; padding: 10px; text-align: left; font-weight: bold; border: 1px solid #2c3e50; }}
                table.data td {{ border: 1px solid #bdc3c7; padding: 10px; }}
                table.data tr:nth-child(even) {{ background-color: #f9f9f9; }}
                
                .totals {{ width: 100%; }}
                .totals td {{ padding: 8px; text-align: right; }}
                .totals .label {{ font-weight: bold; color: #34495e; }}
                .totals .value {{ font-size: 14px; width: 120px; }}
                .totals .grand-total {{ font-size: 16px; font-weight: bold; color: #27ae60; border-top: 2px solid #bdc3c7; padding-top: 10px; }}
                .totals .balance {{ font-size: 16px; font-weight: bold; color: {'#27ae60' if inv.pay_state.value == 'PAGADO' else '#e74c3c'}; }}
                
                .footer {{ margin-top: 50px; text-align: center; font-size: 11px; color: #95a5a6; border-top: 1px solid #ecf0f1; padding-top: 20px; }}
                .status-badge {{ display: inline-block; padding: 5px 10px; background-color: {'#27ae60' if inv.pay_state.value == 'PAGADO' else '#f39c12'}; color: white; font-weight: bold; border-radius: 3px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <table>
                    <tr>
                        <td>
                            <h1>JOLDENS</h1>
                            <h3>Dental Management System</h3>
                            <p style="margin-top:10px; font-size: 12px; color: #7f8c8d;">
                                Tel: +1 234 567 8900<br/>
                                Email: facturacion@joldens.com<br/>
                                Web: www.joldens.com
                            </p>
                        </td>
                        <td class="invoice-title">
                            <h2>FACTURA COMERCIAL</h2>
                            <p><b>NRO:</b> FAC-{inv.id_invoice}</p>
                            <p><b>FECHA:</b> {inv.invoice_date.strftime('%Y-%m-%d')}</p>
                            <p><b>ESTADO:</b> <span class="status-badge">{inv.pay_state.value}</span></p>
                        </td>
                    </tr>
                </table>
            </div>
            
            <table class="info-section">
                <tr>
                    <td style="padding-right: 10px;">
                        <div class="box">
                            <h4>FACTURAR A:</h4>
                            <p><b>Clínica:</b> {clin_name}<br/>
                            <b>Doctor:</b> Dr. {doc_name}</p>
                        </div>
                    </td>
                    <td style="padding-left: 10px;">
                        <div class="box">
                            <h4>DETALLES DEL SERVICIO:</h4>
                            <p><b>Orden de Ref:</b> ORD-{inv.id_job}<br/>
                            <b>Fecha Orden:</b> {inv.job.entry_date if inv.job else 'N/A'}</p>
                        </div>
                    </td>
                </tr>
            </table>
            
            <table class="data">
                <tr>
                    <th style="width: 10%;">CANT.</th>
                    <th style="width: 50%;">DESCRIPCIÓN DEL TRATAMIENTO</th>
                    <th style="width: 20%; text-align: right;">PRECIO UNIT.</th>
                    <th style="width: 20%; text-align: right;">SUBTOTAL</th>
                </tr>
        """
        
        if inv.job:
            for p in inv.job.products:
                pname = p.product.name if p.product else "Desconocido"
                subt = p.quantity * float(p.historic_price)
                html += f"""
                <tr>
                    <td style="text-align: center;">{p.quantity}</td>
                    <td>{pname} <span style="font-size:10px; color:#7f8c8d;">(ID:{p.id_product})</span></td>
                    <td style="text-align: right;">${float(p.historic_price):,.2f}</td>
                    <td style="text-align: right;">${subt:,.2f}</td>
                </tr>
                """
                
        html += f"""
            </table>
            
            <table class="totals">
                <tr>
                    <td class="label">Monto Total Facturado:</td>
                    <td class="value grand-total">${inv.amount:,.2f}</td>
                </tr>
                <tr>
                    <td class="label">Saldo Restante por Cobrar:</td>
                    <td class="value balance">${inv.lending_balance:,.2f}</td>
                </tr>
            </table>
            
            <h4 style="color: #2c3e50; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; margin-top: 40px;">Registro de Pagos Aplicados</h4>
            <table class="data" style="width: 70%;">
                <tr>
                    <th>Fecha y Hora</th>
                    <th>Método de Pago</th>
                    <th style="text-align: right;">Monto Abonado</th>
                </tr>
        """
        if not payments:
            html += "<tr><td colspan='3' style='text-align: center; color: #7f8c8d;'>No se han registrado pagos para esta factura.</td></tr>"
        else:
            for pay in payments:
                html += f"""
                <tr>
                    <td>{pay.pay_date.strftime('%Y-%m-%d %H:%M')}</td>
                    <td>{pay.payment_type.value}</td>
                    <td style="text-align: right;">${pay.payment_amount:,.2f}</td>
                </tr>
                """
                
        html += """
            </table>
            
            <div class="footer">
                Documento generado electrónicamente por <b>Joldens Dental Management System</b>.<br/>
                Powered by Antigravity Technology.
            </div>
        </body>
        </html>
        """
        
        document = QTextDocument()
        document.setHtml(html)
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        
        document.print(printer)
        session.close()
        
        # Abrir carpeta
        import sys
        import subprocess
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folder_path])
        else:
            subprocess.Popen(['xdg-open', folder_path])
        
        QMessageBox.information(self, "PDF Generado Automáticamente", f"Factura profesional guardada en:\n{file_path}\n\nSe ha abierto la carpeta para su conveniencia.")
