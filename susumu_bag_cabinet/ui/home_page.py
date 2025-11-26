"""
Home page UI for Susumu Bag Cabinet.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from susumu_bag_cabinet.ui.custom_widgets import SquareButton


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

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)

        # Record button
        self.record_btn = SquareButton("🟥 記録する", size=200, font_size=18)
        self.record_btn.clicked.connect(self.record_clicked)
        button_layout.addWidget(self.record_btn)

        # Browse button
        self.browse_btn = SquareButton("🟦 記録をみる", size=200, font_size=18)
        self.browse_btn.clicked.connect(self.browse_clicked)
        button_layout.addWidget(self.browse_btn)

        # Settings button
        self.settings_btn = SquareButton("⚙ 設定をひらく", size=200, font_size=18)
        self.settings_btn.clicked.connect(self.settings_clicked)
        button_layout.addWidget(self.settings_btn)

        # Add button layout to main layout (centered)
        layout.addLayout(button_layout)

        layout.addStretch()

        self.setLayout(layout)
