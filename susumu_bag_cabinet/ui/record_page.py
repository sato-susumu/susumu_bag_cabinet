"""
Record page UI for Susumu Bag Cabinet.
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal, QTimer, Qt
from susumu_bag_cabinet.utils.config import Config
from susumu_bag_cabinet.utils.bag_utils import generate_folder_name
from susumu_bag_cabinet.ui.ui_helpers import (
    DialogHelper, FontHelper, FileOperationHelper, ButtonStyleHelper
)
from susumu_bag_cabinet.ui.custom_widgets import (
    LargeButton, CountdownDialog, IndeterminateProgressDialog
)


class RecordPage(QWidget):
    """Page for recording bag files."""

    # Signals
    home_clicked = Signal()

    def __init__(self, config: Config):
        """Initialize the record page.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config
        self.process = None
        self.recording = False
        self.start_time = None
        self.output_path = None

        # Timer for updating elapsed time and file size
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_recording_info)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("記録する")
        title.setFont(FontHelper.create_title_font())
        layout.addWidget(title)

        # Settings group
        settings_group = QGroupBox("記録設定")
        settings_layout = QVBoxLayout()

        # Folder path
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("保存先フォルダ:"))
        self.folder_label = QLabel()
        self.folder_label.setWordWrap(True)
        folder_layout.addWidget(self.folder_label, 1)
        settings_layout.addLayout(folder_layout)

        # Label input
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("ラベル (任意):"))
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("例: 廊下テスト、屋外走行1")
        label_layout.addWidget(self.label_input, 1)
        settings_layout.addLayout(label_layout)

        # Save path (will be shown when recording)
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存先パス:"))
        self.path_label = QLabel("-")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("QLabel { color: #666; }")
        path_layout.addWidget(self.path_label, 1)
        settings_layout.addLayout(path_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Status group
        status_group = QGroupBox("記録ステータス")
        status_layout = QVBoxLayout()

        # Status
        status_layout.addWidget(QLabel("状態:"))
        self.status_label = QLabel("待機中")
        self.status_label.setFont(FontHelper.create_status_font())
        status_layout.addWidget(self.status_label)

        # Elapsed time
        status_layout.addWidget(QLabel("経過時間:"))
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(FontHelper.create_status_font())
        status_layout.addWidget(self.time_label)

        # File size
        status_layout.addWidget(QLabel("ファイルサイズ:"))
        self.size_label = QLabel("-")
        self.size_label.setFont(FontHelper.create_status_font())
        status_layout.addWidget(self.size_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        self.start_btn = LargeButton("記録開始")
        self.start_btn.clicked.connect(self._start_recording)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = LargeButton("記録停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_recording)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # Home button
        self.home_btn = QPushButton("ホームへ戻る")
        self.home_btn.setMinimumHeight(50)
        self.home_btn.clicked.connect(self._on_home_clicked)
        layout.addWidget(self.home_btn)

        self.setLayout(layout)

        # Initialize display
        self._update_folder_display()

    def _update_folder_display(self):
        """Update the folder path display."""
        folder = self.config.get_bag_folder()
        self.folder_label.setText(folder)

    def _start_recording(self):
        """Start recording."""
        # Generate output path (folder name only)
        folder = Path(self.config.get_bag_folder())
        folder.mkdir(parents=True, exist_ok=True)

        label = self.label_input.text().strip()
        robot_name = self.config.get_robot_name()
        include_robot = self.config.get_folder_include_robot_name()

        # Generate folder name (without .mcap extension)
        folder_name = generate_folder_name(label, robot_name, include_robot)
        self.output_path = folder / folder_name

        # Start ros2 bag record
        cmd = [
            'ros2', 'bag', 'record',
            '-a',  # Record all topics
            '--storage', 'mcap',
            '-o', str(self.output_path)
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(folder)
            )

            self.recording = True
            self.start_time = datetime.now()

            # Update UI
            self.status_label.setText("記録中")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            # Show folder path without .mcap extension
            folder_path = str(self.output_path)
            self.path_label.setText(folder_path)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.home_btn.setEnabled(False)
            self.label_input.setEnabled(False)

            # Start update timer
            self.update_timer.start(1000)  # Update every second

        except Exception as e:
            DialogHelper.show_error(
                self,
                "エラー",
                f"記録の開始に失敗しました:\n{str(e)}"
            )

    def _stop_recording(self):
        """Stop recording."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

            self.process = None

        self.recording = False
        self.update_timer.stop()

        # Update UI
        self.status_label.setText("停止済み")
        self.status_label.setStyleSheet("QLabel { color: gray; }")
        self.path_label.setText("-")  # Reset path
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.home_btn.setEnabled(True)
        self.label_input.setEnabled(True)

        # Show completion message with auto-close countdown
        self._show_completion_dialog()

    def _update_recording_info(self):
        """Update elapsed time and file size during recording."""
        if not self.recording or not self.start_time:
            return

        # Update elapsed time
        elapsed = datetime.now() - self.start_time
        time_str = FileOperationHelper.format_elapsed_time(elapsed.seconds)
        self.time_label.setText(time_str)

        # Update file size (ROS2 bag creates a folder structure)
        if self.output_path and self.output_path.exists():
            if self.output_path.is_dir():
                # Sum up all files in the bag directory
                size = sum(f.stat().st_size for f in self.output_path.rglob('*') if f.is_file())
                self.size_label.setText(self._format_size(size))
            elif self.output_path.is_file():
                # Standalone file (less common)
                size = self.output_path.stat().st_size
                self.size_label.setText(self._format_size(size))

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        return FileOperationHelper.format_size(size_bytes)

    def _on_home_clicked(self):
        """Handle home button click."""
        if self.recording:
            DialogHelper.show_warning(
                self,
                "警告",
                "記録を停止してから戻ってください。"
            )
            return

        self.home_clicked.emit()

    def closeEvent(self, event):
        """Handle window close event."""
        if self.recording:
            reply = QMessageBox.question(
                self,
                "確認",
                "記録中です。記録を停止してから閉じてください。\n本当に閉じますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._stop_recording()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def _show_completion_dialog(self):
        """Show completion dialog with auto-close countdown."""
        dialog = CountdownDialog(
            "記録完了",
            f"記録が完了しました。\n{self.output_path}",
            countdown_seconds=3,
            parent=self
        )
        dialog.show_with_countdown()

    def refresh_config(self):
        """Refresh the display based on current config."""
        self._update_folder_display()
