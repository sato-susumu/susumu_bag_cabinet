"""
Background worker for scanning bag files and extracting metadata.
"""

from PySide6.QtCore import QObject, Signal, QThread
from typing import List, Dict, Any
from susumu_bag_cabinet.utils.bag_utils import scan_bag_folder, get_bag_info


class BagScannerWorker(QObject):
    """Worker for scanning bag files in background."""

    # Signals
    scan_started = Signal()
    scan_completed = Signal(list)  # List of file paths
    file_info_updated = Signal(str, dict)  # path, info dict
    progress = Signal(int, int)  # current, total
    error = Signal(str)

    def __init__(self, folder_path: str):
        """Initialize the worker.

        Args:
            folder_path: Path to the folder to scan
        """
        super().__init__()
        self.folder_path = folder_path
        self._should_stop = False

    def stop(self):
        """Request the worker to stop."""
        self._should_stop = True

    def scan(self):
        """Scan the folder and get file information."""
        try:
            self.scan_started.emit()

            # First, quickly scan for all bag files
            bag_files = scan_bag_folder(self.folder_path)
            self.scan_completed.emit(bag_files)

            # Then, get detailed info for each file
            total = len(bag_files)
            for i, bag_path in enumerate(bag_files):
                if self._should_stop:
                    break

                self.progress.emit(i + 1, total)

                # Get detailed information
                info = get_bag_info(bag_path)
                self.file_info_updated.emit(bag_path, info)

        except Exception as e:
            self.error.emit(str(e))


class BagScanner(QObject):
    """Manager for bag scanning operations."""

    # Forward signals from worker
    scan_started = Signal()
    scan_completed = Signal(list)
    file_info_updated = Signal(str, dict)
    progress = Signal(int, int)
    error = Signal(str)

    def __init__(self, folder_path: str):
        """Initialize the scanner.

        Args:
            folder_path: Path to the folder to scan
        """
        super().__init__()
        self.folder_path = folder_path
        self.thread: QThread = None
        self.worker: BagScannerWorker = None

    def start(self):
        """Start scanning in a background thread."""
        if self.thread is not None and self.thread.isRunning():
            return

        self.thread = QThread()
        self.worker = BagScannerWorker(self.folder_path)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.scan_started.connect(self.scan_started)
        self.worker.scan_completed.connect(self.scan_completed)
        self.worker.file_info_updated.connect(self.file_info_updated)
        self.worker.progress.connect(self.progress)
        self.worker.error.connect(self.error)

        # Connect thread signals
        self.thread.started.connect(self.worker.scan)
        self.worker.scan_completed.connect(self._on_scan_completed)

        self.thread.start()

    def _on_scan_completed(self):
        """Handle scan completion (but don't quit thread yet - still processing metadata)."""
        pass

    def stop(self):
        """Stop the scanning thread."""
        if self.worker:
            self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def update_folder(self, folder_path: str):
        """Update the folder path and restart scanning."""
        self.stop()
        self.folder_path = folder_path
        self.start()
