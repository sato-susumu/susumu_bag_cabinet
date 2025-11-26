"""
Recordingモデル - ROS2 bag記録セッションを管理
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer


class Recording(QObject):
    """ROS2 bag記録セッションを管理するモデルクラス"""

    # シグナル
    recording_started = Signal()  # 記録開始
    recording_stopped = Signal()  # 記録停止
    status_updated = Signal(str)  # ステータス更新（記録中、停止済みなど）
    elapsed_time_updated = Signal(int)  # 経過時間更新（秒）
    file_size_updated = Signal(int)  # ファイルサイズ更新（バイト）
    error_occurred = Signal(str)  # エラー発生

    def __init__(self):
        """初期化"""
        super().__init__()
        self._process: Optional[subprocess.Popen] = None
        self._is_recording = False
        self._start_time: Optional[datetime] = None
        self._output_path: Optional[Path] = None
        self._label: str = ""

        # タイマー（1秒ごとに更新）
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_status)

    @property
    def is_recording(self) -> bool:
        """記録中かどうか"""
        return self._is_recording

    @property
    def output_path(self) -> Optional[Path]:
        """出力先パス"""
        return self._output_path

    @property
    def label(self) -> str:
        """記録ラベル"""
        return self._label

    def start(
        self,
        output_path: Path,
        label: str = "",
        topics: str = "-a"
    ) -> bool:
        """
        記録を開始

        Args:
            output_path: 出力先パス（フォルダ）
            label: 記録ラベル
            topics: 記録するトピック（デフォルト: -a すべて）

        Returns:
            成功した場合True
        """
        if self._is_recording:
            self.error_occurred.emit("既に記録中です")
            return False

        try:
            # 出力先フォルダを作成
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # ros2 bag recordコマンドを実行
            cmd = [
                'ros2', 'bag', 'record',
                topics,
                '--storage', 'mcap',
                '-o', str(output_path)
            ]

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(output_path.parent)
            )

            self._is_recording = True
            self._start_time = datetime.now()
            self._output_path = output_path
            self._label = label

            # タイマーを開始
            self._update_timer.start(1000)  # 1秒ごと

            self.recording_started.emit()
            self.status_updated.emit("記録中")
            return True

        except Exception as e:
            self.error_occurred.emit(f"記録の開始に失敗しました: {str(e)}")
            return False

    def stop(self) -> bool:
        """
        記録を停止

        Returns:
            成功した場合True
        """
        if not self._is_recording:
            return False

        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

            self._process = None

        self._is_recording = False
        self._update_timer.stop()

        self.recording_stopped.emit()
        self.status_updated.emit("停止済み")
        return True

    def _update_status(self):
        """ステータスを更新（タイマーから呼ばれる）"""
        if not self._is_recording or not self._start_time:
            return

        # 経過時間を更新
        elapsed = datetime.now() - self._start_time
        self.elapsed_time_updated.emit(elapsed.seconds)

        # ファイルサイズを更新
        if self._output_path and self._output_path.exists():
            if self._output_path.is_dir():
                # ディレクトリ内のすべてのファイルのサイズを合計
                size = sum(
                    f.stat().st_size
                    for f in self._output_path.rglob('*')
                    if f.is_file()
                )
                self.file_size_updated.emit(size)
            elif self._output_path.is_file():
                size = self._output_path.stat().st_size
                self.file_size_updated.emit(size)

    def get_elapsed_time(self) -> int:
        """
        経過時間を取得

        Returns:
            経過時間（秒）
        """
        if not self._start_time:
            return 0
        elapsed = datetime.now() - self._start_time
        return elapsed.seconds

    def cleanup(self):
        """クリーンアップ"""
        if self._is_recording:
            self.stop()
