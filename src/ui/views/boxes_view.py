from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QTabWidget, QLineEdit, QComboBox, QGridLayout, QSpinBox)
from PyQt6.QtCore import Qt

from src.database.session import SessionLocal
from src.repositories.box_repository import BoxRepository

class BoxesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Gestor de Cajas del Laboratorio")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Listado
        self.tab_list = QWidget()
        self.setup_list_tab()
        self.tabs.addTab(self.tab_list, "🗄️ Cajas Registradas")
        
        # Tab 2: Crear
        self.tab_create = QWidget()
        self.setup_create_tab()
        self.tabs.addTab(self.tab_create, "➕ Añadir Caja")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(lambda idx: self.load_data() if idx == 0 else None)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        # Filtros Superiores
        top_controls = QHBoxLayout()
        
        self.cb_filter_color = QComboBox()
        self.cb_filter_color.addItems(["Todos los colores", "Roja", "Verde", "Amarilla", "Gris", "Azul"])
        
        btn_filter = QPushButton("Filtrar Cajas Libres")
        btn_filter.setObjectName("ActionBtn")
        btn_filter.clicked.connect(self.load_data)
        
        top_controls.addWidget(QLabel("Filtro:"))
        top_controls.addWidget(self.cb_filter_color)
        top_controls.addStretch()
        top_controls.addWidget(btn_filter)
        
        layout.addLayout(top_controls)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Color Físico", "Número", "Estado de Uso"])
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
        
        self.cb_color = QComboBox()
        self.cb_color.addItems(["roja", "verde", "amarilla", "gris", "azul"])
        
        self.inp_number = QSpinBox()
        self.inp_number.setRange(1, 9999)
        self.inp_number.setValue(1)
        
        form_layout.addWidget(QLabel("Color de la Caja Física:"), 0, 0)
        form_layout.addWidget(self.cb_color, 0, 1)
        form_layout.addWidget(QLabel("Número Designado:"), 1, 0)
        form_layout.addWidget(self.inp_number, 1, 1)
        
        layout.addLayout(form_layout)
        
        btn_save = QPushButton("Guardar Nueva Caja")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.create_box_action)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        self.tab_create.setLayout(layout)

    def load_data(self):
        session = SessionLocal()
        box_repo = BoxRepository(session)
        
        filter_color = self.cb_filter_color.currentText()
        if filter_color == "Todos los colores":
            boxes = box_repo.list_available_box()
            # En la vida real haríamos una funcion list_all_boxes() 
            # Pero usando los recursos del Repositorio disponibles (disponibles / disponibles por color)
        else:
            boxes = box_repo.list_available_box_by_color(filter_color.lower())
            
        self.table.setRowCount(0)
        # Note: box_repo.list_available_box actually queries WHERE status = LIBRE. So it's technically a filter.
        # Let's write a direct query here to prevent omitting occupied boxes from the global panel if needed, 
        # or we just rely on what the Repo provides like the user requested.
        
        for row, box in enumerate(boxes):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(box.id_box)))
            self.table.setItem(row, 1, QTableWidgetItem(box.color.value.capitalize()))
            self.table.setItem(row, 2, QTableWidgetItem(str(box.number)))
            
            estado = box.status.value
            item_estado = QTableWidgetItem(estado)
            if estado == "LIBRE": item_estado.setForeground(Qt.GlobalColor.darkGreen)
            elif estado == "OCUPADA": item_estado.setForeground(Qt.GlobalColor.darkRed)
            
            self.table.setItem(row, 3, item_estado)
            
        session.close()

    def create_box_action(self):
        color = self.cb_color.currentText()
        numero = self.inp_number.value()
        
        session = SessionLocal()
        box_repo = BoxRepository(session)
        try:
            box_repo.create_box(color, numero)
            QMessageBox.information(self, "Éxito", f"Caja {color} #{numero} añadida a la red.")
            
            self.inp_number.setValue(self.inp_number.value() + 1)
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Fallo al registrar Caja: {e}")
        finally:
            session.close()
