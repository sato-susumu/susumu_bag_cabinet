"""
BrowseController - 閲覧ページのビジネスロジックを管理
"""

from pathlib import Path
from typing import List
from PySide6.QtCore import QObject, Signal
from susumu_bag_cabinet.models.bag_collection import BagCollection
from susumu_bag_cabinet.models.bag_file import BagFile
from susumu_bag_cabinet.utils.bag_operations import compress_bag, repair_bag
from susumu_bag_cabinet.workers.bag_scanner import BagScanner


class BrowseController(QObject):
    """閲覧ページのコントローラークラス"""

    # シグナル
    operation_started = Signal(str)  # 操作開始（操作名）
    operation_progress = Signal(str)  # 操作進捗（メッセージ）
    operation_completed = Signal(str)  # 操作完了（結果メッセージ）
    operation_failed = Signal(str)  # 操作失敗（エラーメッセージ）

    def __init__(self, bag_collection: BagCollection):
        """
        初期化

        Args:
            bag_collection: bagファイルコレクション
        """
        super().__init__()
        self._collection = bag_collection
        self._scanner: BagScanner = None

    @property
    def collection(self) -> BagCollection:
        """bagファイルコレクション"""
        return self._collection

    def start_scan(self):
        """フォルダスキャンを開始"""
        folder = str(self._collection.base_folder)

        # 既存のスキャナーを停止
        if self._scanner:
            self._scanner.stop()

        # 新しいスキャナーを作成
        self._scanner = BagScanner(folder)

        # スキャナーのシグナルをコレクションに接続
        self._scanner.scan_completed.connect(self._on_scan_completed)
        self._scanner.file_info_updated.connect(self._on_file_info_updated)

        self._scanner.start()

    def _on_scan_completed(self, file_paths: List[str]):
        """
        スキャン完了時の処理

        Args:
            file_paths: 見つかったファイルパスのリスト
        """
        # コレクションをクリア
        self._collection.clear()

        # ファイルを追加
        for file_path in file_paths:
            self._collection.add_file(file_path)

    def _on_file_info_updated(self, path: str, info: dict):
        """
        ファイル情報更新時の処理

        Args:
            path: ファイルパス
            info: ファイル情報
        """
        bag_file = self._collection.get_file(path)
        if bag_file:
            bag_file.update_info(info)

    def compress_files(self, files: List[BagFile], compression: str = "zstd"):
        """
        ファイルを圧縮

        Args:
            files: 圧縮するファイルのリスト
            compression: 圧縮形式
        """
        self.operation_started.emit("圧縮")

        success_count = 0
        failed_files = []

        for i, bag_file in enumerate(files):
            self.operation_progress.emit(
                f"圧縮中... ({i+1}/{len(files)})\n{bag_file.name}"
            )

            success, message = compress_bag(str(bag_file.path), compression)
            if success:
                success_count += 1
            else:
                failed_files.append(f"{bag_file.name}: {message}")

        # 結果メッセージを作成
        result_msg = f"圧縮完了: {success_count}/{len(files)}個"
        if failed_files:
            result_msg += "\n\n失敗したファイル:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                result_msg += f"\n...他{len(failed_files) - 5}個"

        self.operation_completed.emit(result_msg)

    def repair_files(self, files: List[BagFile]):
        """
        ファイルを修復

        Args:
            files: 修復するファイルのリスト
        """
        # エラーのあるファイルのみをフィルタ
        files_to_repair = [f for f in files if f.has_integrity_error()]

        if not files_to_repair:
            self.operation_failed.emit(
                "選択されたファイルに修復が必要なものはありません。"
            )
            return

        self.operation_started.emit("修復")

        success_count = 0
        failed_files = []

        for i, bag_file in enumerate(files_to_repair):
            self.operation_progress.emit(
                f"修復中... ({i+1}/{len(files_to_repair)})\n{bag_file.name}"
            )

            success, message = repair_bag(str(bag_file.path))
            if success:
                success_count += 1
            else:
                failed_files.append(f"{bag_file.name}: {message}")

        # 結果メッセージを作成
        result_msg = f"修復完了: {success_count}/{len(files_to_repair)}個"
        if failed_files:
            result_msg += "\n\n失敗したファイル:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                result_msg += f"\n...他{len(failed_files) - 5}個"

        self.operation_completed.emit(result_msg)

    def delete_files(self, files: List[BagFile]):
        """
        ファイルを削除

        Args:
            files: 削除するファイルのリスト
        """
        import shutil

        self.operation_started.emit("削除")

        success_count = 0
        failed_files = []

        for i, bag_file in enumerate(files):
            self.operation_progress.emit(
                f"削除中... ({i+1}/{len(files)})\n{bag_file.name}"
            )

            try:
                if bag_file.path.is_file():
                    bag_file.path.unlink()
                elif bag_file.path.is_dir():
                    shutil.rmtree(bag_file.path)

                # コレクションから削除
                self._collection.remove_file(str(bag_file.path))
                success_count += 1

            except Exception as e:
                failed_files.append(f"{bag_file.name}: {str(e)}")

        # 結果メッセージを作成
        result_msg = f"削除完了: {success_count}/{len(files)}個"
        if failed_files:
            result_msg += "\n\n失敗したファイル:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                result_msg += f"\n...他{len(failed_files) - 5}個"

        self.operation_completed.emit(result_msg)

    def stop_scan(self):
        """スキャンを停止"""
        if self._scanner:
            self._scanner.stop()
