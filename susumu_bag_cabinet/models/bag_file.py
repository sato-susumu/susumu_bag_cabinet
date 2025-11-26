"""
BagFileモデル - ROS2 bagファイルのデータモデル
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal


class BagFile(QObject):
    """ROS2 bagファイルを表すモデルクラス"""

    # シグナル: データが更新されたときに発信
    data_updated = Signal()

    def __init__(self, file_path: str):
        """
        初期化

        Args:
            file_path: bagファイルのパス
        """
        super().__init__()
        self._path = Path(file_path)
        self._size: int = 0
        self._format: str = "Unknown"
        self._start_time: Optional[datetime] = None
        self._compression: str = "未チェック"
        self._is_valid: str = "未チェック"

    @property
    def path(self) -> Path:
        """ファイルパス"""
        return self._path

    @property
    def name(self) -> str:
        """ファイル名"""
        return self._path.name

    @property
    def size(self) -> int:
        """ファイルサイズ（バイト）"""
        return self._size

    @size.setter
    def size(self, value: int):
        """ファイルサイズを設定"""
        self._size = value
        self.data_updated.emit()

    @property
    def format(self) -> str:
        """ファイル形式（MCAP/DB3など）"""
        return self._format

    @format.setter
    def format(self, value: str):
        """ファイル形式を設定"""
        self._format = value
        self.data_updated.emit()

    @property
    def start_time(self) -> Optional[datetime]:
        """記録開始時刻"""
        return self._start_time

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        """記録開始時刻を設定"""
        self._start_time = value
        self.data_updated.emit()

    @property
    def compression(self) -> str:
        """圧縮状態"""
        return self._compression

    @compression.setter
    def compression(self, value: str):
        """圧縮状態を設定"""
        self._compression = value
        self.data_updated.emit()

    @property
    def is_valid(self) -> str:
        """整合性状態"""
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: str):
        """整合性状態を設定"""
        self._is_valid = value
        self.data_updated.emit()

    def update_info(self, info: Dict[str, Any]):
        """
        bag情報を一括更新

        Args:
            info: bag_utils.get_bag_info()から取得した情報辞書
        """
        self._size = info.get("size", 0)
        self._format = info.get("format", "Unknown")
        self._start_time = info.get("start_time")
        self._compression = info.get("compression", "未チェック")
        self._is_valid = info.get("is_valid", "未チェック")
        self.data_updated.emit()

    def get_relative_path(self, base_folder: Path) -> str:
        """
        基準フォルダからの相対パスを取得

        Args:
            base_folder: 基準フォルダ

        Returns:
            相対パス文字列
        """
        try:
            return str(self._path.relative_to(base_folder))
        except ValueError:
            return self._path.name

    def has_integrity_error(self) -> bool:
        """
        整合性エラーがあるかチェック

        Returns:
            エラーがある場合True
        """
        return self._is_valid == "NG" or "エラー" in str(self._is_valid)

    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換

        Returns:
            bag情報の辞書
        """
        return {
            "path": str(self._path),
            "size": self._size,
            "format": self._format,
            "start_time": self._start_time,
            "compression": self._compression,
            "is_valid": self._is_valid,
        }
