from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

class AccordionSection(QWidget):
    def __init__(self, title, buttons_data, index_offset, callback_switch_view):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header Button
        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setObjectName("AccordionHeader")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self.toggle_animation)
        layout.addWidget(self.toggle_btn)
        
        # Content Area
        self.content_area = QFrame()
        self.content_area.setObjectName("AccordionContent")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.buttons = []
        for text, rel_index in buttons_data:
            abs_index = index_offset + rel_index
            btn = QPushButton(text)
            btn.setObjectName("SidebarButton")
            btn.setCheckable(True)
            # Use default argument capture lambda
            btn.clicked.connect(lambda checked, idx=abs_index: callback_switch_view(idx))
            self.content_layout.addWidget(btn)
            self.buttons.append((btn, abs_index))
            
        layout.addWidget(self.content_area)
        self.setLayout(layout)
        
        # Animation properties
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # Start Collapsed
        self.content_area.setMaximumHeight(0)
        self.is_expanded = False
        
    def toggle_animation(self):
        # Calculate exactly how much space the content needs dynamically
        content_height = self.content_layout.sizeHint().height()
        if self.is_expanded:
            self.animation.setStartValue(content_height)
            self.animation.setEndValue(0)
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(content_height)
            
        self.is_expanded = not self.is_expanded
        self.animation.start()

    def get_all_buttons(self):
        return [b[0] for b in self.buttons]
