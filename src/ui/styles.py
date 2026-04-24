# Archivo global de estilos de Joldens
# Mantiene una paleta moderna, minimalista y médica en azul/gris/blanco.

GLOBAL_STYLESHEET = """
QMainWindow {
    background-color: #f0f4f8; 
}

QWidget#CentralContainer {
    background-color: white;
    border-radius: 12px;
}

QWidget#Sidebar {
    background-color: #2c3e50;
    min-width: 200px;
    max-width: 250px;
}

QPushButton#AccordionHeader {
    background-color: #243447;
    color: white;
    font-size: 15px;
    font-weight: bold;
    text-align: left;
    padding: 15px 20px;
    border: none;
    border-bottom: 1px solid #1a252f;
}

QPushButton#AccordionHeader:hover {
    background-color: #2c3e50;
}

QPushButton#AccordionHeader:checked {
    background-color: #2980b9;
}

QFrame#AccordionContent {
    background-color: #34495e;
}

QPushButton#SidebarButton {
    background-color: transparent;
    color: #bdc3c7;
    font-size: 13px;
    text-align: left;
    padding: 12px 10px 12px 35px; /* Indentado para parecer un sub-menú */
    border: none;
}

QPushButton#SidebarButton:hover {
    background-color: #3b536b;
    color: white;
}

QPushButton#SidebarButton:checked {
    background-color: #1abc9c;
    color: white;
    border-left: 4px solid white;
}

QLabel {
    color: #2c3e50;
    font-size: 14px;
}

QLabel#Title {
    color: #1a5276; 
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 20px;
}

QLabel#Subtitle {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 15px;
}

/* Tablas */
QTableWidget {
    background-color: white;
    alternate-background-color: #f9fbfb;
    selection-background-color: #3498db;
    selection-color: white;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    gridline-color: #bdc3c7;
}

QListWidget {
    background-color: white;
    color: #2c3e50;
    font-size: 14px;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    padding: 5px;
}

QTableWidget::item, QListWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #2980b9;
    color: white;
    padding: 6px;
    border: 1px solid #2980b9;
    font-weight: bold;
}

/* Botones genéricos estilo Action */
QPushButton#ActionBtn {
    background-color: #2980b9;
    color: white;
    font-size: 13px;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 15px;
    border: none;
}
QPushButton#ActionBtn:hover { background-color: #3498db; }
QPushButton#ActionBtn:pressed { background-color: #1a5276; }

QPushButton#DangerBtn {
    background-color: #e74c3c;
    color: white;
    font-size: 13px;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 15px;
    border: none;
}
QPushButton#DangerBtn:hover { background-color: #c0392b; }

/* Inpus */
QLineEdit, QComboBox {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #2980b9;
}

/* Tabs / Pestañas */
QTabWidget::pane {
    border: 1px solid #dcdde1;
    border-radius: 6px;
    background: white;
}

QTabBar::tab {
    background: #f0f4f8;
    border: 1px solid #dcdde1;
    border-bottom-color: #dcdde1; 
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 8ex;
    padding: 8px 15px;
    color: #2c3e50;
    font-weight: bold;
}

QTabBar::tab:selected {
    background: white;
    border-bottom-color: white; 
    color: #2980b9;
}

QTabBar::tab:hover {
    background: #e1e8ed;
}

"""
