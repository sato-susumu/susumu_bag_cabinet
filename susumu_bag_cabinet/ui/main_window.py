"""
Main window for Susumu Bag Cabinet.
"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
from susumu_bag_cabinet.utils.config import Config
from susumu_bag_cabinet.ui.home_page import HomePage
from susumu_bag_cabinet.ui.record_page import RecordPage
from susumu_bag_cabinet.ui.browse_page import BrowsePage
from susumu_bag_cabinet.ui.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Load configuration
        self.config = Config()

        # Set up window
        self.setWindowTitle("Susumu Bag Cabinet")
        self.resize(1000, 700)

        # Create stacked widget for page navigation
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create pages
        self.home_page = HomePage()
        self.record_page = RecordPage(self.config)
        self.browse_page = BrowsePage(self.config)
        self.settings_page = SettingsPage(self.config)

        # Add pages to stacked widget
        self.home_index = self.stacked_widget.addWidget(self.home_page)
        self.record_index = self.stacked_widget.addWidget(self.record_page)
        self.browse_index = self.stacked_widget.addWidget(self.browse_page)
        self.settings_index = self.stacked_widget.addWidget(self.settings_page)

        # Connect signals
        self._connect_signals()

        # Show home page
        self.stacked_widget.setCurrentIndex(self.home_index)

    def _connect_signals(self):
        """Connect page signals."""
        # Home page navigation
        self.home_page.record_clicked.connect(self._show_record_page)
        self.home_page.browse_clicked.connect(self._show_browse_page)
        self.home_page.settings_clicked.connect(self._show_settings_page)

        # Return to home
        self.record_page.home_clicked.connect(self._show_home_page)
        self.browse_page.home_clicked.connect(self._show_home_page)
        self.settings_page.home_clicked.connect(self._show_home_page)

        # Settings changed
        self.settings_page.settings_changed.connect(self._on_settings_changed)

    def _show_home_page(self):
        """Show the home page."""
        self.stacked_widget.setCurrentIndex(self.home_index)

    def _show_record_page(self):
        """Show the record page."""
        self.record_page.refresh_config()
        self.stacked_widget.setCurrentIndex(self.record_index)

    def _show_browse_page(self):
        """Show the browse page."""
        self.browse_page.refresh_config()
        self.stacked_widget.setCurrentIndex(self.browse_index)

    def _show_settings_page(self):
        """Show the settings page."""
        self.settings_page.refresh_from_config()
        self.stacked_widget.setCurrentIndex(self.settings_index)

    def _on_settings_changed(self):
        """Handle settings change."""
        # Refresh all pages that depend on settings
        self.record_page.refresh_config()
        self.browse_page.refresh_config()

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop any running scanners
        if hasattr(self.browse_page, 'scanner') and self.browse_page.scanner:
            self.browse_page.scanner.stop()

        event.accept()
