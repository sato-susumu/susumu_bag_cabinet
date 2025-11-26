"""
BagCollectionモデル - 複数のbagファイルを管理
"""

from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QObject, Signal
from susumu_bag_cabinet.models.bag_file import BagFile
from susumu_bag_cabinet.utils.bag_utils import scan_bag_folder, get_bag_info


class BagCollection(QObject):
    """複数のbagファイルを管理するコレクションクラス"""

    # シグナル
    collection_updated = Signal()  # コレクションが更新された
    file_added = Signal(BagFile)  # ファイルが追加された
    file_removed = Signal(str)  # ファイルが削除された（パス文字列）
    scan_started = Signal()  # スキャン開始
    scan_progress = Signal(int, int)  # スキャン進捗（現在, 合計）
    scan_completed = Signal()  # スキャン完了

    def __init__(self, base_folder: str):
        """
        初期化

        Args:
            base_folder: bagファイルの基準フォルダ
        """
        super().__init__()
        self._base_folder = Path(base_folder)
        self._files: List[BagFile] = []
        self._file_map: dict[str, BagFile] = {}  # パス -> BagFileのマップ

    @property
    def base_folder(self) -> Path:
        """基準フォルダ"""
        return self._base_folder

    @base_folder.setter
    def base_folder(self, value: str):
        """基準フォルダを変更"""
        self._base_folder = Path(value)
        self.collection_updated.emit()

    @property
    def files(self) -> List[BagFile]:
        """すべてのbagファイル"""
        return self._files.copy()

    def get_file(self, path: str) -> Optional[BagFile]:
        """
        パスからbagファイルを取得

        Args:
            path: ファイルパス

        Returns:
            BagFileオブジェクト、見つからない場合None
        """
        return self._file_map.get(path)

    def add_file(self, file_path: str) -> BagFile:
        """
        ファイルを追加

        Args:
            file_path: ファイルパス

        Returns:
            追加されたBagFileオブジェクト
        """
        if file_path in self._file_map:
            return self._file_map[file_path]

        bag_file = BagFile(file_path)
        self._files.append(bag_file)
        self._file_map[file_path] = bag_file
        self.file_added.emit(bag_file)
        self.collection_updated.emit()
        return bag_file

    def remove_file(self, path: str):
        """
        ファイルを削除

        Args:
            path: ファイルパス
        """
        if path in self._file_map:
            bag_file = self._file_map[path]
            self._files.remove(bag_file)
            del self._file_map[path]
            self.file_removed.emit(path)
            self.collection_updated.emit()

    def clear(self):
        """すべてのファイルをクリア"""
        self._files.clear()
        self._file_map.clear()
        self.collection_updated.emit()

    def scan_folder(self):
        """
        基準フォルダをスキャンしてbagファイルを検索
        （同期処理 - UIスレッドでは使用しないこと）
        """
        self.scan_started.emit()
        self.clear()

        # フォルダをスキャン
        file_paths = scan_bag_folder(str(self._base_folder))

        # ファイルを追加
        for i, file_path in enumerate(file_paths):
            self.add_file(file_path)
            self.scan_progress.emit(i + 1, len(file_paths))

        self.scan_completed.emit()

    def update_file_info(self, path: str):
        """
        指定されたファイルの情報を更新
        （同期処理 - UIスレッドでは使用しないこと）

        Args:
            path: ファイルパス
        """
        bag_file = self.get_file(path)
        if bag_file:
            info = get_bag_info(path)
            bag_file.update_info(info)

    def get_files_with_errors(self) -> List[BagFile]:
        """
        整合性エラーのあるファイルを取得

        Returns:
            エラーのあるBagFileのリスト
        """
        return [f for f in self._files if f.has_integrity_error()]

    def count(self) -> int:
        """
        ファイル数を取得

        Returns:
            ファイル数
        """
        return len(self._files)
