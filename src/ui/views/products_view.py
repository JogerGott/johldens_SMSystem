from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QDoubleSpinBox, QSpinBox, QGridLayout)
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
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(lambda idx: self.load_data() if idx == 0 else None)

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
        self.inp_price.setRange(0.00, 99999.99)
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

    def load_data(self):
        session = SessionLocal()
        prod_repo = ProductRepository(session)
        products = prod_repo.list_active_products()
        
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
