#!/usr/bin/env python3
"""
Main entry point for Susumu Bag Cabinet application.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from susumu_bag_cabinet.ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Enable high DPI scaling for better display on modern screens
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Susumu Bag Cabinet")
    app.setOrganizationName("ROS2")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
