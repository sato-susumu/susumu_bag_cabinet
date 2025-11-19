"""
Home page UI for Susumu Bag Cabinet.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class HomePage(QWidget):
    """Home page with navigation buttons."""

    # Signals
    record_clicked = Signal()
    browse_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self):
        """Initialize the home page."""
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("Susumu Bag Cabinet")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addStretch()

        # Record button
        self.record_btn = QPushButton("🟥 記録する")
        self.record_btn.setMinimumHeight(100)
        self.record_btn.setMinimumWidth(400)
        btn_font = QFont()
        btn_font.setPointSize(18)
        self.record_btn.setFont(btn_font)
        self.record_btn.clicked.connect(self.record_clicked)
        layout.addWidget(self.record_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Browse button
        self.browse_btn = QPushButton("🟦 記録をみる")
        self.browse_btn.setMinimumHeight(100)
        self.browse_btn.setMinimumWidth(400)
        self.browse_btn.setFont(btn_font)
        self.browse_btn.clicked.connect(self.browse_clicked)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Settings button
        self.settings_btn = QPushButton("⚙ 設定をひらく")
        self.settings_btn.setMinimumHeight(100)
        self.settings_btn.setMinimumWidth(400)
        self.settings_btn.setFont(btn_font)
        self.settings_btn.clicked.connect(self.settings_clicked)
        layout.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.setLayout(layout)
