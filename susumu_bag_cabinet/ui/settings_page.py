"""
Settings page UI for Susumu Bag Cabinet.
"""

import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QGroupBox, QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from susumu_bag_cabinet.utils.config import Config
from susumu_bag_cabinet.ui.ui_helpers import (
    DialogHelper, FontHelper, ButtonStyleHelper
)
from susumu_bag_cabinet.ui.custom_widgets import (
    LargeButton, CountdownDialog
)


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
        title.setFont(FontHelper.create_title_font())
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
        self.include_robot_checkbox.setChecked(self.config.get_folder_include_robot_name())
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

        # glim_rosbag settings group
        glim_group = QGroupBox("glim_rosbag")
        glim_layout = QVBoxLayout()

        glim_path_layout = QHBoxLayout()
        glim_path_layout.addWidget(QLabel("config_path:"))
        self.glim_config_input = QLineEdit()
        self.glim_config_input.setText(self.config.get_glim_config_path())
        glim_path_layout.addWidget(self.glim_config_input, 1)

        glim_browse_btn = QPushButton("参照...")
        glim_browse_btn.clicked.connect(self._browse_glim_config)
        glim_path_layout.addWidget(glim_browse_btn)

        glim_layout.addLayout(glim_path_layout)
        glim_group.setLayout(glim_layout)
        layout.addWidget(glim_group)

        # Desktop shortcut group
        shortcut_group = QGroupBox("デスクトップショートカット")
        shortcut_layout = QVBoxLayout()

        shortcut_btn = QPushButton("デスクトップにショートカットを作成")
        shortcut_btn.setMinimumHeight(40)
        shortcut_btn.clicked.connect(self._create_desktop_shortcut)
        shortcut_layout.addWidget(shortcut_btn)

        shortcut_group.setLayout(shortcut_layout)
        layout.addWidget(shortcut_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = LargeButton("保存してホームへ", min_height=50, font_size=12)
        save_btn.clicked.connect(self._save_and_go_home)
        button_layout.addWidget(save_btn)

        cancel_btn = LargeButton("キャンセル", min_height=50, font_size=12)
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

    def _browse_glim_config(self):
        """Open folder browser dialog for glim config path."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "glim config_pathを選択",
            self.glim_config_input.text()
        )

        if folder:
            self.glim_config_input.setText(folder)

    def _update_preview(self):
        """Update filename preview."""
        robot_name = self.robot_input.text().strip()
        include_robot = self.include_robot_checkbox.isChecked()

        if include_robot and robot_name:
            preview = f"{robot_name}_YYYYMMDD_HHMMSS_<ラベル>"
        else:
            preview = "YYYYMMDD_HHMMSS_<ラベル>"

        self.preview_label.setText(preview)

    def _test_foxglove(self):
        """Test Foxglove Studio launch."""
        command = self.foxglove_input.text().strip()
        if not command:
            DialogHelper.show_warning(
                self,
                "警告",
                "Foxgloveコマンドを入力してください。"
            )
            return

        try:
            # Try to launch Foxglove
            subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            DialogHelper.show_info(
                self,
                "成功",
                "Foxglove Studioの起動コマンドが実行されました。"
            )
        except Exception as e:
            DialogHelper.show_error(
                self,
                "エラー",
                f"Foxglove Studioの起動に失敗しました:\n{str(e)}"
            )

    def _create_desktop_shortcut(self):
        """Create desktop shortcut for the application."""
        import os
        from pathlib import Path

        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            desktop_path = Path.home() / "デスクトップ"

        if not desktop_path.exists():
            DialogHelper.show_warning(
                self,
                "警告",
                "デスクトップフォルダが見つかりません。"
            )
            return

        # Get the application directory
        app_dir = Path(__file__).parent.parent.parent

        # Create shell script path
        script_path = app_dir / "run_susumu_bag_cabinet.sh"

        # Create shell script content
        # Using bash -i ensures .bashrc is loaded, which sets up ROS2 environment
        shell_script_content = f"""#!/bin/bash

cd {app_dir}

python3 -m susumu_bag_cabinet.main
"""

        # Create .desktop file content
        desktop_file_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Susumu Bag Cabinet
Comment=ROS2 Bag管理アプリケーション
Exec=bash -i {script_path}
Icon=folder
Terminal=false
Categories=Development;Utility;
"""

        desktop_file_path = desktop_path / "susumu_bag_cabinet.desktop"

        try:
            # Write shell script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(shell_script_content)

            # Make shell script executable
            os.chmod(script_path, 0o755)

            # Write .desktop file
            with open(desktop_file_path, 'w', encoding='utf-8') as f:
                f.write(desktop_file_content)

            # Make .desktop file executable
            os.chmod(desktop_file_path, 0o755)

            DialogHelper.show_info(
                self,
                "成功",
                f"デスクトップにショートカットを作成しました。\n{desktop_file_path}"
            )
        except Exception as e:
            DialogHelper.show_error(
                self,
                "エラー",
                f"ショートカットの作成に失敗しました:\n{str(e)}"
            )

    def _save_and_go_home(self):
        """Save settings and go to home."""
        # Validate folder path
        folder = self.folder_input.text().strip()
        if not folder:
            DialogHelper.show_warning(
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
        self.config.set_glim_config_path(self.glim_config_input.text().strip())
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
        self.include_robot_checkbox.setChecked(self.config.get_folder_include_robot_name())
        self.foxglove_input.setText(self.config.get_foxglove_command())
        self.glim_config_input.setText(self.config.get_glim_config_path())

        self.home_clicked.emit()

    def refresh_from_config(self):
        """Refresh UI from current config."""
        self.folder_input.setText(self.config.get_bag_folder())
        self.robot_input.setText(self.config.get_robot_name())
        self.include_robot_checkbox.setChecked(self.config.get_folder_include_robot_name())
        self.foxglove_input.setText(self.config.get_foxglove_command())
        self.glim_config_input.setText(self.config.get_glim_config_path())
        self._update_preview()

    def _show_completion_dialog(self):
        """Show completion dialog with auto-close countdown."""
        dialog = CountdownDialog(
            "保存完了",
            "設定を保存しました。",
            countdown_seconds=3,
            parent=self
        )
        dialog.show_with_countdown()
