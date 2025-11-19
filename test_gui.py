#!/usr/bin/env python3
"""
GUI test script - launches the application for a few seconds.
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from susumu_bag_cabinet.ui.main_window import MainWindow


def test_gui():
    """Test GUI by launching and closing after a short time."""
    app = QApplication(sys.argv)
    app.setApplicationName("Susumu Bag Cabinet - Test")

    window = MainWindow()
    window.show()

    print("GUI window opened successfully!")
    print(f"Window title: {window.windowTitle()}")
    print(f"Window size: {window.size().width()}x{window.size().height()}")
    print("Testing page navigation...")

    # Test navigation after a short delay
    def navigate_to_record():
        print("Navigating to record page...")
        window._show_record_page()

    def navigate_to_browse():
        print("Navigating to browse page...")
        window._show_browse_page()

    def navigate_to_settings():
        print("Navigating to settings page...")
        window._show_settings_page()

    def navigate_to_home():
        print("Navigating back to home page...")
        window._show_home_page()

    def close_app():
        print("Test completed successfully!")
        print("Closing application...")
        app.quit()

    # Schedule navigation tests
    QTimer.singleShot(500, navigate_to_record)
    QTimer.singleShot(1000, navigate_to_browse)
    QTimer.singleShot(1500, navigate_to_settings)
    QTimer.singleShot(2000, navigate_to_home)
    QTimer.singleShot(2500, close_app)

    return app.exec()


if __name__ == "__main__":
    try:
        test_gui()
        print("\n✓ GUI test passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
