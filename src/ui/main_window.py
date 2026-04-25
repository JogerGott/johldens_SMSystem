import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFrame, QStackedWidget, QMessageBox, QDialog
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtCore import Qt, QTimer

# Importar Componentes
from src.ui.styles import GLOBAL_STYLESHEET
from src.database.session import SessionLocal
from src.ui.components.accordion import AccordionSection

# Modulos Visuales
from src.ui.views.clinics_view import ClinicsView
from src.ui.views.doctors_view import DoctorsView
from src.ui.views.patients_view import PatientsView
from src.ui.views.boxes_view import BoxesView
from src.ui.views.products_view import ProductsView
from src.ui.views.jobs_view import JobsView
from src.ui.views.invoices_view import InvoicesView
from src.ui.views.payments_view import PaymentsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("State Management System - Joldens Dental")
        self.setGeometry(100, 100, 1100, 750) 
        
        main_base = QWidget()
        self.setCentralWidget(main_base)
        
        # Layout maestro (Horizontal: Sidebar Izquierda, Contenido Derecha)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_base.setLayout(main_layout)

        # 1. Sidebar (Menú Izquierdo)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Joldens\nSystem")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin: 25px 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)

        # Base button (Out of accordion)
        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_dashboard.setObjectName("SidebarButton")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        sidebar_layout.addWidget(self.btn_dashboard)

        # Listado General para agrupar luego iterativamente
        self.all_sidebar_buttons = [self.btn_dashboard]

        # Configuración de los Grupos Acordeón y sus Sub-Botones correspondientes
        self.accordions = []
        
        # Grupo 1: Gestión de Clientes (Offset empiza en 1 ya que Dash es 0)
        btn_data_clientes = [("👨‍⚕️ Doctores", 0), ("🏥 Clínicas", 1), ("🧑‍🤝‍🧑 Pacientes", 2)]
        grp_clientes = AccordionSection("▼ Gestión de Clientes", btn_data_clientes, index_offset=1, callback_switch_view=self.switch_view)
        
        # Grupo 2: Laboratorio (Offset: 4)
        btn_data_lab = [("📦 Trabajos (Jobs)", 0), ("🗄️ Cajas (Boxes)", 1), ("🦷 Productos", 2)]
        grp_lab = AccordionSection("▼ Laboratorio", btn_data_lab, index_offset=4, callback_switch_view=self.switch_view)
        
        # Grupo 3: Facturas (Offset: 7)
        btn_data_facturas = [("💳 Facturación", 0), ("💰 Pagos y Abonos", 1)]
        grp_facturas = AccordionSection("▼ Facturación", btn_data_facturas, index_offset=7, callback_switch_view=self.switch_view)

        self.accordions.extend([grp_clientes, grp_lab, grp_facturas])
        for acc in self.accordions:
            sidebar_layout.addWidget(acc)
            self.all_sidebar_buttons.extend(acc.get_all_buttons())
        
        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)

        # 2. Area Central de Contenido (Stacked Widget)
        self.content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("CentralContainer") 
        
        # Conectar Visores
        self.setup_views()

        content_layout.addWidget(self.stacked_widget)
        self.content_area.setLayout(content_layout)

        # Ensamblar
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area, stretch=1) 

        # Select first nav
        self.switch_view(0)

    def setup_views(self):
        # Llenamos el stack widget con layouts dummy y las views reales, acorde al index absoluto
        # 0 = Dashboard
        lbl1 = QLabel("Dashboard (Resumen)...")
        lbl1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(lbl1)

        # == [CLIENTES] ==
        # 1 = Doctores
        self.doctors_view = DoctorsView()
        self.stacked_widget.addWidget(self.doctors_view)
        # 2 = Clinicas
        self.clinics_view = ClinicsView()
        self.stacked_widget.addWidget(self.clinics_view)
        # 3 = Pacientes
        self.patients_view = PatientsView()
        self.stacked_widget.addWidget(self.patients_view)

        # == [LABORATORIO] ==
        # 4 = Jobs
        self.jobs_view = JobsView()
        self.stacked_widget.addWidget(self.jobs_view)
        # 5 = Cajas
        self.boxes_view = BoxesView()
        self.stacked_widget.addWidget(self.boxes_view)
        # 6 = Productos
        self.products_view = ProductsView()
        self.stacked_widget.addWidget(self.products_view)

        # == [FACTURACION] ==
        # 7 = Facturas
        self.invoices_view = InvoicesView()
        self.stacked_widget.addWidget(self.invoices_view)
        # 8 = Pagos
        self.payments_view = PaymentsView()
        self.stacked_widget.addWidget(self.payments_view)

    def switch_view(self, index):
        for i, b in enumerate(self.all_sidebar_buttons):
            # Abs index matches the loop position mapping
            b.setChecked(i == index)
        self.stacked_widget.setCurrentIndex(index)

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(550, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a252f;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QLabel#Title {
                color: #ecf0f1;
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QLabel#Subtitle {
                color: #bdc3c7;
                font-size: 16px;
                margin-bottom: 20px;
            }
            QLabel#Powered {
                color: #3498db;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton#StartBtn {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#StartBtn:hover {
                background-color: #2980b9;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        lbl_welcome = QLabel("WELCOME TO JOLDENS")
        lbl_welcome.setObjectName("Title")
        lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_sub = QLabel("Advanced Dental Laboratory Management System")
        lbl_sub.setObjectName("Subtitle")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spacer for centering
        layout.addStretch()
        layout.addWidget(lbl_welcome)
        layout.addWidget(lbl_sub)
        
        # Button container to center it
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("GET STARTED")
        self.btn_start.setObjectName("StartBtn")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()

        lbl_powered = QLabel("POWERED BY ASCENT")
        lbl_powered.setObjectName("Powered")
        lbl_powered.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_powered)
        
        layout.setContentsMargins(40, 40, 40, 20)
        self.setLayout(layout)

def start_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.showMaximized()
    
    # Mostrar el diálogo premium de bienvenida
    welcome = WelcomeDialog(window)
    welcome.exec()
    
    sys.exit(app.exec())
