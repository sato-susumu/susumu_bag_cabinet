"""
Browse page UI for Susumu Bag Cabinet.
"""

import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QCheckBox, QDialog, QTextEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from susumu_bag_cabinet.utils.config import Config
from susumu_bag_cabinet.utils.bag_utils import format_size, format_duration
from susumu_bag_cabinet.utils.bag_operations import repair_bag
from susumu_bag_cabinet.workers.bag_scanner import BagScanner
from susumu_bag_cabinet.ui.custom_widgets import (
    LargeButton, DeleteButton, IndeterminateProgressDialog
)


class BrowsePage(QWidget):
    """Page for browsing bag files."""

    # Signals
    home_clicked = Signal()

    def __init__(self, config: Config):
        """Initialize the browse page.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config
        self.scanner = None
        self.bag_files = []
        self.file_info = {}  # path -> info dict

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title and refresh
        header_layout = QHBoxLayout()
        title = QLabel("記録をみる")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("更新")
        refresh_btn.clicked.connect(self._refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Folder path
        self.folder_label = QLabel()
        self.folder_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.folder_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "選択", "ファイル名", "サイズ", "記録開始日時", "記録時間",
            "形式"
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Allow manual resize
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Set initial width for filename column (wider to accommodate full paths)
        self.table.setColumnWidth(1, 400)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)  # ヘッダークリックでソート可能に
        self.table.cellClicked.connect(self._on_table_cell_clicked)

        layout.addWidget(self.table)

        # Operation buttons
        button_layout1 = QHBoxLayout()

        self.select_all_btn = QPushButton("全選択")
        self.select_all_btn.clicked.connect(self._select_all)
        button_layout1.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("選択解除")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        button_layout1.addWidget(self.deselect_all_btn)

        button_layout1.addStretch()

        layout.addLayout(button_layout1)

        button_layout2 = QHBoxLayout()

        self.info_btn = LargeButton("Info", min_height=40, font_size=12)
        self.info_btn.clicked.connect(self._show_info)
        button_layout2.addWidget(self.info_btn)

        self.open_btn = LargeButton("オープンする", min_height=40, font_size=12)
        self.open_btn.clicked.connect(self._open_selected)
        button_layout2.addWidget(self.open_btn)

        self.repair_btn = LargeButton("修復を試みる", min_height=40, font_size=12)
        self.repair_btn.clicked.connect(self._repair_selected)
        button_layout2.addWidget(self.repair_btn)

        self.foxglove_btn = LargeButton("Foxgloveで再生", min_height=40, font_size=12)
        self.foxglove_btn.clicked.connect(self._play_in_foxglove)
        button_layout2.addWidget(self.foxglove_btn)

        layout.addLayout(button_layout2)

        # Delete button (in a separate row for safety)
        button_layout3 = QHBoxLayout()
        button_layout3.addStretch()

        self.delete_btn = QPushButton("選択したファイルを削除")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self._delete_selected)
        button_layout3.addWidget(self.delete_btn)

        button_layout3.addStretch()
        layout.addLayout(button_layout3)

        # Home button
        self.home_btn = QPushButton("ホームへ戻る")
        self.home_btn.setMinimumHeight(40)
        self.home_btn.clicked.connect(self.home_clicked)
        layout.addWidget(self.home_btn)

        self.setLayout(layout)

        # Update folder display
        self._update_folder_display()

        # Initially disable file-operation buttons
        self._update_button_states()

    def _update_folder_display(self):
        """Update the folder path display."""
        folder = self.config.get_bag_folder()
        self.folder_label.setText(f"フォルダ: {folder}")

    def start_scan(self):
        """Start scanning for bag files."""
        folder = self.config.get_bag_folder()

        # Stop existing scanner if any
        if self.scanner:
            self.scanner.stop()

        # Create new scanner
        self.scanner = BagScanner(folder)
        self.scanner.scan_started.connect(self._on_scan_started)
        self.scanner.scan_completed.connect(self._on_scan_completed)
        self.scanner.file_info_updated.connect(self._on_file_info_updated)
        self.scanner.progress.connect(self._on_progress)
        self.scanner.error.connect(self._on_error)

        self.scanner.start()

    def _on_scan_started(self):
        """Handle scan start."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate

    def _on_scan_completed(self, file_paths):
        """Handle scan completion.

        Args:
            file_paths: List of bag file paths found
        """
        self.bag_files = file_paths
        self._populate_table()

        if file_paths:
            self.progress_bar.setMaximum(len(file_paths))
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.setVisible(False)

    def _on_file_info_updated(self, path, info):
        """Handle file info update.

        Args:
            path: File path
            info: Information dictionary
        """
        self.file_info[path] = info
        self._update_table_row(path, info)

    def _on_progress(self, current, total):
        """Handle progress update.

        Args:
            current: Current progress
            total: Total items
        """
        self.progress_bar.setValue(current)
        if current >= total:
            self.progress_bar.setVisible(False)

    def _on_error(self, error_msg):
        """Handle error.

        Args:
            error_msg: Error message
        """
        QMessageBox.warning(self, "エラー", f"スキャン中にエラーが発生しました:\n{error_msg}")

    def _populate_table(self):
        """Populate the table with bag files."""
        self.table.setRowCount(len(self.bag_files))

        for row, file_path in enumerate(self.bag_files):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self._update_button_states)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)

            # Filename (relative path from base folder + actual .mcap filename)
            base_folder = Path(self.config.get_bag_folder())
            file_path_obj = Path(file_path)

            try:
                # Get relative path of the directory/file
                relative_dir = file_path_obj.relative_to(base_folder)

                if file_path_obj.is_dir():
                    # Find the first .mcap or .mcap.* file in the directory
                    mcap_files = [f for f in file_path_obj.iterdir()
                                  if f.is_file() and '.mcap' in f.name]
                    if mcap_files:
                        # Sort to get consistent ordering
                        mcap_files.sort()
                        # Combine relative directory path with .mcap filename
                        display_name = str(relative_dir / mcap_files[0].name)
                    else:
                        # Fallback to directory name if no .mcap file found
                        display_name = str(relative_dir)
                else:
                    display_name = str(relative_dir)
            except ValueError:
                # If file is not in base folder, use absolute path
                if file_path_obj.is_dir():
                    mcap_files = [f for f in file_path_obj.iterdir()
                                  if f.is_file() and '.mcap' in f.name]
                    if mcap_files:
                        mcap_files.sort()
                        display_name = str(file_path_obj / mcap_files[0].name)
                    else:
                        display_name = str(file_path_obj)
                else:
                    display_name = str(file_path_obj)

            filename_item = QTableWidgetItem(display_name)
            # Set tooltip to show full path on hover
            filename_item.setToolTip(display_name)
            self.table.setItem(row, 1, filename_item)

            # サイズ（後で更新される）
            self.table.setItem(row, 2, QTableWidgetItem("-"))

            # 記録開始日時（後で更新される）
            self.table.setItem(row, 3, QTableWidgetItem("読込中..."))

            # 記録時間（後で更新される）
            self.table.setItem(row, 4, QTableWidgetItem("-"))

            # 形式（後で更新される）
            self.table.setItem(row, 5, QTableWidgetItem("-"))

        # Update button states after populating table
        self._update_button_states()

    def _update_table_row(self, path, info):
        """Update a table row with file information.

        Args:
            path: File path
            info: Information dictionary
        """
        # Find the row for this file
        base_folder = Path(self.config.get_bag_folder())
        file_path_obj = Path(path)

        try:
            # Get relative path of the directory/file
            relative_dir = file_path_obj.relative_to(base_folder)

            if file_path_obj.is_dir():
                # Find the first .mcap or .mcap.* file in the directory
                mcap_files = [f for f in file_path_obj.iterdir()
                              if f.is_file() and '.mcap' in f.name]
                if mcap_files:
                    mcap_files.sort()
                    # Combine relative directory path with .mcap filename
                    display_name = str(relative_dir / mcap_files[0].name)
                else:
                    # Fallback to directory name if no .mcap file found
                    display_name = str(relative_dir)
            else:
                display_name = str(relative_dir)
        except ValueError:
            # If file is not in base folder, use absolute path
            if file_path_obj.is_dir():
                mcap_files = [f for f in file_path_obj.iterdir()
                              if f.is_file() and '.mcap' in f.name]
                if mcap_files:
                    mcap_files.sort()
                    display_name = str(file_path_obj / mcap_files[0].name)
                else:
                    display_name = str(file_path_obj)
            else:
                display_name = str(file_path_obj)

        row = -1
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 1)
            if item and display_name == item.text():
                row = i
                break

        if row == -1:
            return

        # Update filename tooltip (in case it wasn't set)
        filename_item = self.table.item(row, 1)
        if filename_item:
            filename_item.setToolTip(display_name)

        # Update size
        size_str = format_size(info.get("size", 0))
        self.table.setItem(row, 2, QTableWidgetItem(size_str))

        # 記録開始日時を更新
        start_time = info.get("start_time")
        if start_time:
            if isinstance(start_time, str):
                time_str = start_time
            else:
                time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "不明"
        self.table.setItem(row, 3, QTableWidgetItem(time_str))

        # 記録時間を更新
        duration_str = format_duration(info.get("duration"))
        self.table.setItem(row, 4, QTableWidgetItem(duration_str))

        # 形式を更新
        format_str = info.get("format", "Unknown")
        self.table.setItem(row, 5, QTableWidgetItem(format_str))

        # Update button states (repair button needs to check if any files have errors)
        self._update_button_states()

    def _get_selected_files(self):
        """Get list of selected file paths."""
        selected = []
        base_folder = Path(self.config.get_bag_folder())

        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    display_name = self.table.item(row, 1).text()
                    # Find full path by matching the display name
                    for file_path in self.bag_files:
                        file_path_obj = Path(file_path)

                        try:
                            # Get relative path of the directory/file
                            relative_dir = file_path_obj.relative_to(base_folder)

                            # Check if it's a directory with .mcap files
                            if file_path_obj.is_dir():
                                mcap_files = [f for f in file_path_obj.iterdir()
                                              if f.is_file() and '.mcap' in f.name]
                                if mcap_files:
                                    mcap_files.sort()
                                    # Compare with relative path + mcap filename
                                    check_name = str(relative_dir / mcap_files[0].name)
                                    if check_name == display_name:
                                        selected.append(file_path)
                                        break
                                else:
                                    if str(relative_dir) == display_name:
                                        selected.append(file_path)
                                        break
                            # Check if it's a standalone file
                            elif str(relative_dir) == display_name:
                                selected.append(file_path)
                                break
                        except ValueError:
                            # Handle absolute paths
                            if file_path_obj.is_dir():
                                mcap_files = [f for f in file_path_obj.iterdir()
                                              if f.is_file() and '.mcap' in f.name]
                                if mcap_files:
                                    mcap_files.sort()
                                    check_name = str(file_path_obj / mcap_files[0].name)
                                    if check_name == display_name:
                                        selected.append(file_path)
                                        break
                            elif str(file_path_obj) == display_name:
                                selected.append(file_path)
                                break
        return selected

    def _on_table_cell_clicked(self, row, column):
        """Handle table cell click to toggle checkbox."""
        checkbox_widget = self.table.cellWidget(row, 0)
        if checkbox_widget:
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                # Toggle checkbox state
                checkbox.setChecked(not checkbox.isChecked())

    def _select_all(self):
        """Select all checkboxes."""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
        self._update_button_states()

    def _deselect_all(self):
        """Deselect all checkboxes."""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
        self._update_button_states()

    def _open_selected(self):
        """Open selected files in file manager."""
        selected = self._get_selected_files()
        if not selected:
            QMessageBox.information(self, "情報", "ファイルが選択されていません。")
            return

        # Open each selected file/directory in file manager
        for file_path in selected:
            try:
                path_obj = Path(file_path)

                # Use xdg-open on Linux to open the directory in file manager
                if path_obj.is_dir():
                    # Open directory
                    subprocess.Popen(['xdg-open', str(path_obj)])
                elif path_obj.is_file():
                    # Open parent directory and select the file
                    subprocess.Popen(['xdg-open', str(path_obj.parent)])
                else:
                    QMessageBox.warning(
                        self,
                        "警告",
                        f"ファイルが見つかりません:\n{file_path}"
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "エラー",
                    f"ファイルを開けませんでした:\n{file_path}\n\n{str(e)}"
                )

    def _show_info(self):
        """Show mcap info for selected file."""
        selected = self._get_selected_files()

        if len(selected) == 0:
            QMessageBox.information(self, "情報", "ファイルが選択されていません。")
            return

        if len(selected) > 1:
            QMessageBox.information(self, "情報", "1つのファイルのみを選択してください。")
            return

        file_path = selected[0]
        path_obj = Path(file_path)

        # Find the actual .mcap file
        mcap_file = None
        if path_obj.is_dir():
            # Find .mcap or .mcap.* files in directory
            mcap_files = [f for f in path_obj.iterdir()
                          if f.is_file() and '.mcap' in f.name and f.name != 'metadata.yaml']
            if mcap_files:
                mcap_files.sort()
                mcap_file = mcap_files[0]
        elif path_obj.is_file():
            mcap_file = path_obj

        if not mcap_file:
            QMessageBox.warning(
                self,
                "警告",
                "MCAPファイルが見つかりません。"
            )
            return

        # Run mcap info command
        try:
            result = subprocess.run(
                ['mcap', 'info', str(mcap_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
            else:
                output = f"エラーが発生しました:\n{result.stderr}"
        except FileNotFoundError:
            output = "mcapコマンドが見つかりません。\nmcap CLIツールをインストールしてください。"
        except subprocess.TimeoutExpired:
            output = "コマンドがタイムアウトしました。"
        except Exception as e:
            output = f"エラーが発生しました:\n{str(e)}"

        # Show result in dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"MCAP Info - {mcap_file.name}")
        dialog.resize(800, 600)

        layout = QVBoxLayout()

        # Text area for output
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(output)
        text_edit.setFont(QFont("Monospace", 20))
        layout.addWidget(text_edit)

        # Close button
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def _repair_selected(self):
        """Repair selected bag files."""
        selected = self._get_selected_files()
        if not selected:
            QMessageBox.information(self, "情報", "ファイルが選択されていません。")
            return

        # Filter only files with integrity issues
        files_to_repair = []
        for file_path in selected:
            if file_path in self.file_info:
                is_valid = self.file_info[file_path].get("is_valid", "")
                if is_valid == "NG" or "エラー" in str(is_valid):
                    files_to_repair.append(file_path)

        if not files_to_repair:
            QMessageBox.information(
                self,
                "情報",
                "選択されたファイルに修復が必要なものはありません。\n整合性チェックで「NG」と表示されたファイルのみ修復できます。"
            )
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "修復の確認",
            f"{len(files_to_repair)}個のファイルを修復します。\n\nバックアップが作成され、修復されたファイルは別名で保存されます。\n続行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Create and show progress dialog immediately
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QCoreApplication

        progress = QProgressDialog(
            "修復処理を開始しています...",
            None,  # No cancel button
            0,
            0,  # 0 to 0 = indeterminate (busy indicator)
            self
        )
        progress.setWindowTitle("修復中")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(False)
        progress.setAutoClose(False)
        progress.setMinimumWidth(400)
        progress.setValue(0)  # Force display
        progress.show()
        progress.raise_()
        progress.activateWindow()
        QCoreApplication.processEvents()

        # Process files
        success_count = 0
        failed_files = []

        for i, file_path in enumerate(files_to_repair):
            # Update progress
            filename = Path(file_path).name
            progress.setLabelText(f"修復中... ({i+1}/{len(files_to_repair)})\n{filename}")
            QCoreApplication.processEvents()

            success, message = repair_bag(file_path)
            if success:
                success_count += 1
            else:
                failed_files.append(f"{Path(file_path).name}: {message}")

        progress.close()

        # Show results
        result_msg = f"修復完了: {success_count}/{len(files_to_repair)}個"
        if failed_files:
            result_msg += "\n\n失敗したファイル:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                result_msg += f"\n...他{len(failed_files) - 5}個"

        QMessageBox.information(self, "修復結果", result_msg)
        self._refresh()

    def _play_in_foxglove(self):
        """Play selected file in Foxglove Studio."""
        selected = self._get_selected_files()

        if len(selected) == 0:
            QMessageBox.information(self, "情報", "ファイルが選択されていません。")
            return

        if len(selected) > 1:
            QMessageBox.warning(
                self,
                "警告",
                "ファイルを1つだけ選択してください。"
            )
            return

        file_path = selected[0]
        command = self.config.get_foxglove_command()

        try:
            # Open Foxglove with the bag file path directly
            # Foxglove can handle both .mcap files and directory-based bags
            path_obj = Path(file_path)
            mcap_file_to_open = None

            # If it's a .mcap file, use it directly
            if path_obj.is_file() and path_obj.suffix == '.mcap':
                mcap_file_to_open = str(path_obj)
            # If it's a directory, check for .mcap files inside
            elif path_obj.is_dir():
                # Look for .mcap file in directory (including nested patterns like *_0.mcap)
                mcap_files = list(path_obj.glob('*.mcap'))
                # Also look for *_0.mcap pattern (common in ROS2 bags)
                if not mcap_files:
                    mcap_files = list(path_obj.glob('*_0.mcap'))

                if mcap_files:
                    mcap_file_to_open = str(mcap_files[0])
                else:
                    # No .mcap file found - check if compressed files exist
                    compressed_files = list(path_obj.glob('*.mcap.zstd')) + list(path_obj.glob('*.mcap.lz4'))
                    if compressed_files:
                        raise FileNotFoundError(
                            f"このbagファイルは圧縮されているため、Foxgloveで直接開けません。\n"
                            f"「修復を試みる」機能で展開してから再度お試しください。\n\n"
                            f"圧縮ファイル: {compressed_files[0].name}"
                        )
                    else:
                        # No .mcap file found - show helpful error
                        all_files = list(path_obj.glob('*'))
                        file_list = ', '.join([f.name for f in all_files[:5]])
                        raise FileNotFoundError(
                            f"ディレクトリ内に開けるMCAPファイルが見つかりません。\n"
                            f"ディレクトリ: {path_obj}\n"
                            f"見つかったファイル: {file_list}"
                        )
            else:
                raise FileNotFoundError(f"ファイルまたはディレクトリが見つかりません: {file_path}")

            # Launch Foxglove with the MCAP file
            if mcap_file_to_open:
                print(f"Opening Foxglove with: {command} {mcap_file_to_open}")  # Debug
                subprocess.Popen([command, mcap_file_to_open])

        except Exception as e:
            QMessageBox.critical(
                self,
                "エラー",
                f"Foxglove Studioの起動に失敗しました:\n{str(e)}"
            )

    def _delete_selected(self):
        """Delete selected bag files."""
        selected = self._get_selected_files()
        if not selected:
            QMessageBox.information(self, "情報", "ファイルが選択されていません。")
            return

        # Show warning and confirm
        file_list = "\n".join([f"- {Path(p).name}" for p in selected[:10]])
        if len(selected) > 10:
            file_list += f"\n... 他{len(selected) - 10}個"

        reply = QMessageBox.warning(
            self,
            "削除の確認",
            f"{len(selected)}個のファイルを完全に削除します。\nこの操作は元に戻せません！\n\n削除されるファイル:\n{file_list}\n\n本当に削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Create progress dialog
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QCoreApplication
        import time

        progress = QProgressDialog(
            "削除処理を開始しています...",
            None,  # No cancel button
            0,
            0,  # 0 to 0 = indeterminate (busy indicator)
            self
        )
        progress.setWindowTitle("削除中")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(False)
        progress.setAutoClose(False)
        progress.setMinimumWidth(400)
        progress.show()
        QCoreApplication.processEvents()
        time.sleep(0.1)
        QCoreApplication.processEvents()

        # Delete files
        success_count = 0
        failed_files = []

        for i, file_path in enumerate(selected):
            # Update progress
            filename = Path(file_path).name
            progress.setLabelText(f"削除中... ({i+1}/{len(selected)})\n{filename}")
            QCoreApplication.processEvents()

            try:
                import shutil
                path_obj = Path(file_path)
                if path_obj.is_file():
                    path_obj.unlink()
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj)
                success_count += 1
            except Exception as e:
                failed_files.append(f"{filename}: {str(e)}")

        progress.close()

        # Show results
        result_msg = f"削除完了: {success_count}/{len(selected)}個"
        if failed_files:
            result_msg += "\n\n失敗したファイル:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                result_msg += f"\n...他{len(failed_files) - 5}個"

        QMessageBox.information(self, "削除結果", result_msg)
        self._refresh()

    def _refresh(self):
        """Refresh the file list."""
        self._update_folder_display()
        self.file_info.clear()
        self.start_scan()

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Refresh when page is shown
        self._refresh()

    def refresh_config(self):
        """Refresh based on current config."""
        self._update_folder_display()

    def _update_button_states(self):
        """Update button states based on file selection."""
        selected_files = self._get_selected_files()
        has_selection = len(selected_files) > 0

        # Check if any selected files have integrity issues
        has_error_files = False
        for file_path in selected_files:
            if file_path in self.file_info:
                is_valid = self.file_info[file_path].get("is_valid", "")
                if is_valid == "NG" or "エラー" in str(is_valid):
                    has_error_files = True
                    break

        # Enable/disable buttons based on selection
        self.info_btn.setEnabled(len(selected_files) == 1)  # Only for single file
        self.open_btn.setEnabled(has_selection)
        self.repair_btn.setEnabled(has_error_files)  # Only enable if there are files with errors
        self.foxglove_btn.setEnabled(len(selected_files) == 1)  # Only for single file
        self.delete_btn.setEnabled(has_selection)
        self.deselect_all_btn.setEnabled(has_selection)
