import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

# Estética Panel Médico Moderno solicitada en los Requerimientos
STYLESHEET = """
QMainWindow {
    background-color: #f0f4f8; /* Un gris muy claro/azulado de fondo principal */
}

QWidget#CentralContainer {
    background-color: white;
    border-radius: 12px;
    margin: 20px;
}

QLabel {
    color: #2c3e50;
    font-size: 14px;
}

QLabel#Title {
    color: #1a5276; /* Azul médico profunfo */
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 20px;
}

QPushButton {
    background-color: #2980b9; /* Azul primario */
    color: white;
    font-size: 14px;
    font-weight: bold;
    border-radius: 6px;
    padding: 10px 20px;
    border: none;
}

QPushButton:hover {
    background-color: #1abc9c; /* Al pasar el mouse, cambia a verde médico limpio */
}

QPushButton:pressed {
    background-color: #16a085; /* Verde más oscuro al clickear */
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("State Management System - Joldens Dental")
        self.setGeometry(100, 100, 950, 700) # Tamaño moderno
        
        # Widget Base Principal y su configuración estética
        main_base = QWidget()
        self.setCentralWidget(main_base)
        
        # El layout superior que contendrá los paneles con márgenes
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_base.setLayout(main_layout)

        # Widget Central (Blanco con bordes redondeados sobre el panel gris)
        self.central_container = QWidget()
        self.central_container.setObjectName("CentralContainer")
        
        # Layout del container interior
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_container.setLayout(container_layout)

        # Labels del Diseño
        self.label_title = QLabel("Dashboard - Joldens Management")
        self.label_title.setObjectName("Title")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label_subtitle = QLabel("Panel de gestión médica de base de datos local y estado de envíos.")
        self.label_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")

        # Botones Principales
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.btn_patients = QPushButton("Gestionar Pacientes")
        self.btn_jobs = QPushButton("📦 Trabajos & Envíos (Jobs)")
        self.btn_invoices = QPushButton("Facturación & Pagos")
        
        # TODO: Conectar los botones en iteraciones futuras a sus pantallas respectivas
        self.btn_jobs.clicked.connect(self.open_jobs_view)

        buttons_layout.addWidget(self.btn_patients)
        buttons_layout.addWidget(self.btn_jobs)
        buttons_layout.addWidget(self.btn_invoices)

        # Ensamblar
        container_layout.addWidget(self.label_title)
        container_layout.addWidget(self.label_subtitle)
        container_layout.addLayout(buttons_layout)

        main_layout.addWidget(self.central_container)

    def open_jobs_view(self):
        self.label_title.setText("Cargando Panel de Jobs...")

def start_app():
    app = QApplication(sys.argv)
    
    # Inyectar CSS global
    app.setStyleSheet(STYLESHEET)
    
    # Aplicar fuente moderna tipo sans-serif limpia
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
