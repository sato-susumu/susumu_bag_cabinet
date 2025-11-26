"""
RecordController - 記録ページのビジネスロジックを管理
"""

from pathlib import Path
from PySide6.QtCore import QObject, Signal
from susumu_bag_cabinet.models.recording import Recording
from susumu_bag_cabinet.utils.bag_utils import generate_folder_name


class RecordController(QObject):
    """記録ページのコントローラークラス"""

    # シグナル（Recordingモデルから転送）
    recording_started = Signal()
    recording_stopped = Signal()
    status_updated = Signal(str)
    elapsed_time_updated = Signal(int)
    file_size_updated = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, base_folder: str, robot_name: str = "", include_robot: bool = False):
        """
        初期化

        Args:
            base_folder: 保存先フォルダ
            robot_name: ロボット名
            include_robot: ロボット名を含めるかどうか
        """
        super().__init__()
        self._recording = Recording()
        self._base_folder = Path(base_folder)
        self._robot_name = robot_name
        self._include_robot = include_robot

        # Recordingモデルのシグナルを転送
        self._recording.recording_started.connect(self.recording_started)
        self._recording.recording_stopped.connect(self.recording_stopped)
        self._recording.status_updated.connect(self.status_updated)
        self._recording.elapsed_time_updated.connect(self.elapsed_time_updated)
        self._recording.file_size_updated.connect(self.file_size_updated)
        self._recording.error_occurred.connect(self.error_occurred)

    @property
    def recording(self) -> Recording:
        """Recordingモデル"""
        return self._recording

    @property
    def base_folder(self) -> Path:
        """保存先フォルダ"""
        return self._base_folder

    @base_folder.setter
    def base_folder(self, value: str):
        """保存先フォルダを設定"""
        self._base_folder = Path(value)

    @property
    def robot_name(self) -> str:
        """ロボット名"""
        return self._robot_name

    @robot_name.setter
    def robot_name(self, value: str):
        """ロボット名を設定"""
        self._robot_name = value

    @property
    def include_robot(self) -> bool:
        """ロボット名を含めるか"""
        return self._include_robot

    @include_robot.setter
    def include_robot(self, value: bool):
        """ロボット名を含めるかを設定"""
        self._include_robot = value

    def start_recording(self, label: str = "") -> bool:
        """
        記録を開始

        Args:
            label: 記録ラベル

        Returns:
            成功した場合True
        """
        # フォルダ名を生成
        folder_name = generate_folder_name(
            label=label,
            robot_name=self._robot_name,
            include_robot=self._include_robot
        )

        # 出力パスを作成
        output_path = self._base_folder / folder_name

        # 記録を開始
        return self._recording.start(output_path, label)

    def stop_recording(self) -> bool:
        """
        記録を停止

        Returns:
            成功した場合True
        """
        return self._recording.stop()

    def is_recording(self) -> bool:
        """
        記録中かどうか

        Returns:
            記録中の場合True
        """
        return self._recording.is_recording

    def get_output_path(self) -> str:
        """
        現在の出力パスを取得

        Returns:
            出力パス（文字列）
        """
        if self._recording.output_path:
            return str(self._recording.output_path)
        return ""

    def format_elapsed_time(self) -> str:
        """
        経過時間をフォーマット

        Returns:
            HH:MM:SS形式の文字列
        """
        seconds = self._recording.get_elapsed_time()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        ファイルサイズをフォーマット

        Args:
            size_bytes: サイズ（バイト）

        Returns:
            読みやすい形式の文字列
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
