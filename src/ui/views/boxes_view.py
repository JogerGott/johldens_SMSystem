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
        
        self.tab_update = QWidget()
        self.setup_update_tab()
        self.tabs.addTab(self.tab_update, "🔄 Modificar Estado")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setup_list_tab(self):
        layout = QVBoxLayout()
        
        # Filtros Superiores
        top_controls = QHBoxLayout()
        
        self.cb_filter_color = QComboBox()
        self.cb_filter_color.addItems(["Todos los colores", "ROJA", "VERDE", "AMARILLA", "GRIS", "AZUL"])
        
        self.cb_filter_status = QComboBox()
        self.cb_filter_status.addItems(["Cualquier Estado", "LIBRE", "OCUPADA", "PERDIDA", "INACTIVA"])
        
        self.inp_filter_number = QSpinBox()
        self.inp_filter_number.setRange(0, 9999)
        self.inp_filter_number.setSpecialValueText("Cualquier N°")
        
        btn_filter = QPushButton("Aplicar Filtros")
        btn_filter.setObjectName("ActionBtn")
        btn_filter.clicked.connect(self.load_data)
        
        top_controls.addWidget(QLabel("Color:"))
        top_controls.addWidget(self.cb_filter_color)
        top_controls.addWidget(QLabel("Estado:"))
        top_controls.addWidget(self.cb_filter_status)
        top_controls.addWidget(QLabel("N°:"))
        top_controls.addWidget(self.inp_filter_number)
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
        self.cb_color.addItems(["ROJA", "VERDE", "AMARILLA", "GRIS", "AZUL"])
        
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

    def setup_update_tab(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.cb_update_box = QComboBox()
        self.cb_update_status = QComboBox()
        self.cb_update_status.addItems(["LIBRE", "PERDIDA", "INACTIVA"])
        
        form_layout.addWidget(QLabel("Seleccionar Caja:"), 0, 0)
        form_layout.addWidget(self.cb_update_box, 0, 1)
        form_layout.addWidget(QLabel("Nuevo Estado:"), 1, 0)
        form_layout.addWidget(self.cb_update_status, 1, 1)
        
        layout.addLayout(form_layout)
        
        btn_update = QPushButton("Cambiar Estado")
        btn_update.setObjectName("ActionBtn")
        btn_update.clicked.connect(self.update_box_action)
        
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
        box_repo = BoxRepository(session)
        boxes = box_repo.list_all_boxes()
        
        self.cb_update_box.clear()
        for b in boxes:
            self.cb_update_box.addItem(f"ID {b.id_box} | Caja {b.color.value} N°{b.number} ({b.status.value})", b.id_box)
        session.close()

    def load_data(self):
        session = SessionLocal()
        box_repo = BoxRepository(session)
        
        filter_color = self.cb_filter_color.currentText()
        filter_status = self.cb_filter_status.currentText()
        filter_number = self.inp_filter_number.value()
        
        # We fetch all boxes and filter in python for simplicity, or we could add complex queries to repo.
        boxes = box_repo.list_all_boxes()
        
        filtered_boxes = []
        for b in boxes:
            if filter_color != "Todos los colores" and b.color.value != filter_color:
                continue
            if filter_status != "Cualquier Estado" and b.status.value != filter_status:
                continue
            if filter_number > 0 and b.number != filter_number:
                continue
            filtered_boxes.append(b)
            
        self.table.setRowCount(0)
        
        for row, box in enumerate(filtered_boxes):
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

    def update_box_action(self):
        id_box = self.cb_update_box.currentData()
        status = self.cb_update_status.currentText()
        
        if not id_box: return
        
        session = SessionLocal()
        box_repo = BoxRepository(session)
        try:
            box_repo.change_box_status(id_box, status)
            QMessageBox.information(self, "Éxito", f"Caja actualizada a {status}")
            self.tabs.setCurrentIndex(0)
            self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()
