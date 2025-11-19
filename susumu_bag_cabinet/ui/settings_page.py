"""
Settings page UI for Susumu Bag Cabinet.
"""

import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QGroupBox, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from susumu_bag_cabinet.utils.config import Config


class SettingsPage(QWidget):
    """Page for application settings."""

    # Signals
    home_clicked = Signal()
    settings_changed = Signal()

    def __init__(self, config: Config):
        """Initialize the settings page.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("設定")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Bag folder group
        folder_group = QGroupBox("保存先フォルダ")
        folder_layout = QVBoxLayout()

        folder_input_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setText(self.config.get_bag_folder())
        folder_input_layout.addWidget(self.folder_input, 1)

        browse_btn = QPushButton("参照...")
        browse_btn.clicked.connect(self._browse_folder)
        folder_input_layout.addWidget(browse_btn)

        folder_layout.addLayout(folder_input_layout)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Filename settings group
        filename_group = QGroupBox("ファイル名設定")
        filename_layout = QVBoxLayout()

        # Robot name
        robot_layout = QHBoxLayout()
        robot_layout.addWidget(QLabel("ロボット名:"))
        self.robot_input = QLineEdit()
        self.robot_input.setText(self.config.get_robot_name())
        self.robot_input.setPlaceholderText("例: robot1")
        robot_layout.addWidget(self.robot_input, 1)
        filename_layout.addLayout(robot_layout)

        # Include robot name checkbox
        self.include_robot_checkbox = QCheckBox("ファイル名にロボット名を含める")
        self.include_robot_checkbox.setChecked(self.config.get_filename_include_robot_name())
        filename_layout.addWidget(self.include_robot_checkbox)

        # Preview
        preview_label = QLabel("プレビュー:")
        filename_layout.addWidget(preview_label)
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("QLabel { color: #666; padding: 5px; background-color: #f0f0f0; }")
        self.preview_label.setWordWrap(True)
        filename_layout.addWidget(self.preview_label)

        # Connect signals for preview update
        self.robot_input.textChanged.connect(self._update_preview)
        self.include_robot_checkbox.stateChanged.connect(self._update_preview)

        filename_group.setLayout(filename_layout)
        layout.addWidget(filename_group)

        # Foxglove settings group
        foxglove_group = QGroupBox("Foxglove Studio")
        foxglove_layout = QVBoxLayout()

        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("起動コマンド:"))
        self.foxglove_input = QLineEdit()
        self.foxglove_input.setText(self.config.get_foxglove_command())
        command_layout.addWidget(self.foxglove_input, 1)

        test_btn = QPushButton("テスト起動")
        test_btn.clicked.connect(self._test_foxglove)
        command_layout.addWidget(test_btn)

        foxglove_layout.addLayout(command_layout)
        foxglove_group.setLayout(foxglove_layout)
        layout.addWidget(foxglove_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("保存してホームへ")
        save_btn.setMinimumHeight(50)
        btn_font = QFont()
        btn_font.setPointSize(12)
        save_btn.setFont(btn_font)
        save_btn.clicked.connect(self._save_and_go_home)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setFont(btn_font)
        cancel_btn.clicked.connect(self._cancel)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initialize preview
        self._update_preview()

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "保存先フォルダを選択",
            self.folder_input.text()
        )

        if folder:
            self.folder_input.setText(folder)

    def _update_preview(self):
        """Update filename preview."""
        robot_name = self.robot_input.text().strip()
        include_robot = self.include_robot_checkbox.isChecked()

        if include_robot and robot_name:
            preview = f"{robot_name}_YYYYMMDD_HHMMSS_<ラベル>.mcap"
        else:
            preview = "YYYYMMDD_HHMMSS_<ラベル>.mcap"

        self.preview_label.setText(preview)

    def _test_foxglove(self):
        """Test Foxglove Studio launch."""
        command = self.foxglove_input.text().strip()
        if not command:
            QMessageBox.warning(
                self,
                "警告",
                "Foxgloveコマンドを入力してください。"
            )
            return

        try:
            # Try to launch Foxglove
            subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            QMessageBox.information(
                self,
                "成功",
                "Foxglove Studioの起動コマンドが実行されました。"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "エラー",
                f"Foxglove Studioの起動に失敗しました:\n{str(e)}"
            )

    def _save_and_go_home(self):
        """Save settings and go to home."""
        # Validate folder path
        folder = self.folder_input.text().strip()
        if not folder:
            QMessageBox.warning(
                self,
                "警告",
                "保存先フォルダを指定してください。"
            )
            return

        # Save settings
        self.config.set_bag_folder(folder)
        self.config.set_robot_name(self.robot_input.text().strip())
        self.config.set_filename_include_robot_name(self.include_robot_checkbox.isChecked())
        self.config.set_foxglove_command(self.foxglove_input.text().strip())
        self.config.save()

        # Emit signal
        self.settings_changed.emit()

        # Show completion message with auto-close countdown
        self._show_completion_dialog()

        self.home_clicked.emit()

    def _cancel(self):
        """Cancel and go back to home."""
        # Reload settings from config
        self.folder_input.setText(self.config.get_bag_folder())
        self.robot_input.setText(self.config.get_robot_name())
        self.include_robot_checkbox.setChecked(self.config.get_filename_include_robot_name())
        self.foxglove_input.setText(self.config.get_foxglove_command())

        self.home_clicked.emit()

    def refresh_from_config(self):
        """Refresh UI from current config."""
        self.folder_input.setText(self.config.get_bag_folder())
        self.robot_input.setText(self.config.get_robot_name())
        self.include_robot_checkbox.setChecked(self.config.get_filename_include_robot_name())
        self.foxglove_input.setText(self.config.get_foxglove_command())
        self._update_preview()

    def _show_completion_dialog(self):
        """Show completion dialog with auto-close countdown."""
        from PySide6.QtCore import QTimer

        # Create message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("保存完了")
        msg_box.setIcon(QMessageBox.Icon.Information)

        # Initial message
        countdown = 3
        msg_box.setText(f"設定を保存しました。\n\n({countdown}秒後に自動的に閉じます)")

        # Create timer for countdown
        countdown_timer = QTimer()

        def update_countdown():
            nonlocal countdown
            countdown -= 1
            if countdown > 0:
                msg_box.setText(f"設定を保存しました。\n\n({countdown}秒後に自動的に閉じます)")
            else:
                countdown_timer.stop()
                msg_box.accept()

        countdown_timer.timeout.connect(update_countdown)
        countdown_timer.start(1000)  # Update every second

        # Show dialog (blocks until closed or auto-closed)
        msg_box.exec()

        # Make sure timer is stopped
        countdown_timer.stop()
