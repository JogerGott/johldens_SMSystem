from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QDoubleSpinBox, QSpinBox, QGridLayout,
                             QComboBox)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.product_repository import ProductRepository

class ProductsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Gestor de Productos de Laboratorio")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "📋 Catálogo de Prótesis y Servicios")
        
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Añadir Servicio Nuevo")
        
        self.tab_update = QWidget()
        self.setup_update_tab()
        self.tabs.addTab(self.tab_update, "🔄 Actualizar Producto")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        # Filtro muy básico
        top_controls = QHBoxLayout()
        btn_refresh = QPushButton("Refrescar Catálogo")
        btn_refresh.setObjectName("ActionBtn")
        btn_refresh.clicked.connect(self.load_data)
        top_controls.addStretch()
        top_controls.addWidget(btn_refresh)
        
        layout.addLayout(top_controls)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Servicio", "Descripción", "Precio Base ($)", "Días Fabricación", "Estado"])
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
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej. Corona de Porcelana")
        
        self.inp_price = QDoubleSpinBox()
        self.inp_price.setRange(0.00, 9999999999999.99)
        self.inp_price.setPrefix("$ ")
        
        self.inp_days = QSpinBox()
        self.inp_days.setRange(1, 45)
        self.inp_days.setSuffix(" días")
        
        form_layout.addWidget(QLabel("Nombre del Servicio (Corona, Resina, Acrílico):"), 0, 0)
        form_layout.addWidget(self.inp_name, 0, 1)
        
        form_layout.addWidget(QLabel("Costo Unitario Standard:"), 1, 0)
        form_layout.addWidget(self.inp_price, 1, 1)
        
        form_layout.addWidget(QLabel("Tiempo de Fabricación Esperado:"), 2, 0)
        form_layout.addWidget(self.inp_days, 2, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Añadir al Catálogo")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_product_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)

    def setup_update_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.cb_update_product = QComboBox()
        self.inp_upd_name = QLineEdit()
        self.inp_upd_price = QDoubleSpinBox()
        self.inp_upd_price.setRange(0.00, 9999999999999.99)
        self.inp_upd_price.setPrefix("$ ")
        self.inp_upd_days = QSpinBox()
        self.inp_upd_days.setRange(1, 45)
        self.cb_upd_status = QComboBox()
        self.cb_upd_status.addItems(["Activo", "Descontinuado"])
        
        form_layout.addWidget(QLabel("Seleccionar Producto:"), 0, 0)
        form_layout.addWidget(self.cb_update_product, 0, 1)
        form_layout.addWidget(QLabel("Nuevo Nombre:"), 1, 0)
        form_layout.addWidget(self.inp_upd_name, 1, 1)
        form_layout.addWidget(QLabel("Nuevo Precio:"), 2, 0)
        form_layout.addWidget(self.inp_upd_price, 2, 1)
        form_layout.addWidget(QLabel("Nuevos Días:"), 3, 0)
        form_layout.addWidget(self.inp_upd_days, 3, 1)
        form_layout.addWidget(QLabel("Estado:"), 4, 0)
        form_layout.addWidget(self.cb_upd_status, 4, 1)
        
        self.cb_update_product.currentIndexChanged.connect(self.on_update_product_selected)
        
        layout.addLayout(form_layout)
        
        btn_update = QPushButton("Guardar Cambios")
        btn_update.setObjectName("ActionBtn")
        btn_update.clicked.connect(self.update_product_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_update)
        
        layout.addLayout(btn_layout)
        self.tab_update.setLayout(layout)

    def on_tab_changed(self, index):
        if index == 0:
            self.load_data()
        elif index == 2:
            self.refresh_update_dropdown()

    def refresh_update_dropdown(self):
        session = SessionLocal()
        prod_repo = ProductRepository(session)
        products = prod_repo.list_all_products()
        
        self.cb_update_product.blockSignals(True)
        self.cb_update_product.clear()
        self.cb_update_product.addItem("Seleccione un producto...", None)
        for p in products:
            self.cb_update_product.addItem(f"{p.id_product} - {p.name}", p.id_product)
        self.cb_update_product.blockSignals(False)
        session.close()
        
        self.inp_upd_name.clear()
        self.inp_upd_price.setValue(0)
        self.inp_upd_days.setValue(1)

    def on_update_product_selected(self):
        id_prod = self.cb_update_product.currentData()
        if not id_prod: return
        
        session = SessionLocal()
        prod = ProductRepository(session).check_product(id_prod)
        if prod:
            self.inp_upd_name.setText(prod.name)
            self.inp_upd_price.setValue(float(prod.price))
            self.inp_upd_days.setValue(prod.production_time)
            self.cb_upd_status.setCurrentText("Activo" if prod.status else "Descontinuado")
        session.close()

    def load_data(self):
        session = SessionLocal()
        prod_repo = ProductRepository(session)
        products = prod_repo.list_all_products()
        
        self.table.setRowCount(0)
        for row, prod in enumerate(products):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(prod.id_product)))
            self.table.setItem(row, 1, QTableWidgetItem(prod.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{prod.price:,.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(prod.production_time)))
            
            estado = "Activo" if prod.status else "Descontinuado"
            self.table.setItem(row, 4, QTableWidgetItem(estado))
            
        session.close()

    def create_product_action(self):
        name = self.inp_name.text().strip()
        price = self.inp_price.value()
        days = self.inp_days.value()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del producto no puede estar vacío.")
            return
            
        session = SessionLocal()
        prod_repo = ProductRepository(session)
        try:
            prod_repo.create_product(name, price, days)
            QMessageBox.information(self, "Éxito", f"Producto '{name}' registrado.")
            
            self.inp_name.clear()
            self.inp_price.setValue(0.0)
            self.inp_days.setValue(1)
            
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo guardar el producto:\n\n{e}")
        finally:
            session.close()

    def update_product_action(self):
        id_prod = self.cb_update_product.currentData()
        if not id_prod: return
        
        name = self.inp_upd_name.text().strip()
        price = self.inp_upd_price.value()
        days = self.inp_upd_days.value()
        status = (self.cb_upd_status.currentText() == "Activo")
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            return
            
        session = SessionLocal()
        prod_repo = ProductRepository(session)
        try:
            prod_repo.update_product(id_prod, name, price, days, status)
            QMessageBox.information(self, "Éxito", f"Producto actualizado correctamente.")
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Fallo al actualizar: {e}")
        finally:
            session.close()
