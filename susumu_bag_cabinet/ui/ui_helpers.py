"""
UI共通ヘルパークラスとユーティリティ関数
"""

from PySide6.QtWidgets import (
    QMessageBox, QProgressDialog, QPushButton, QWidget
)
from PySide6.QtCore import Qt, QTimer, QCoreApplication
from PySide6.QtGui import QFont


class DialogHelper:
    """ダイアログ表示のヘルパークラス"""

    @staticmethod
    def show_info(parent: QWidget, title: str, message: str):
        """
        情報ダイアログを表示

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ
        """
        QMessageBox.information(parent, title, message)

    @staticmethod
    def show_warning(parent: QWidget, title: str, message: str):
        """
        警告ダイアログを表示

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ
        """
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_error(parent: QWidget, title: str, message: str):
        """
        エラーダイアログを表示

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ
        """
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_question(
        parent: QWidget,
        title: str,
        message: str,
        default_yes: bool = False
    ) -> bool:
        """
        確認ダイアログを表示

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ
            default_yes: デフォルトをYesにするか

        Returns:
            Yesが選択された場合True
        """
        default_button = (
            QMessageBox.StandardButton.Yes if default_yes
            else QMessageBox.StandardButton.No
        )

        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button
        )

        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def show_countdown_dialog(
        parent: QWidget,
        title: str,
        message: str,
        countdown_seconds: int = 3
    ):
        """
        カウントダウン付き自動クローズダイアログを表示

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ（カウントダウンは自動で追加される）
            countdown_seconds: カウントダウン秒数
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Icon.Information)

        # 初期メッセージ
        countdown = countdown_seconds
        msg_box.setText(f"{message}\n\n({countdown}秒後に自動的に閉じます)")

        # カウントダウンタイマーを作成
        countdown_timer = QTimer()

        def update_countdown():
            nonlocal countdown
            countdown -= 1
            if countdown > 0:
                msg_box.setText(f"{message}\n\n({countdown}秒後に自動的に閉じます)")
            else:
                countdown_timer.stop()
                msg_box.accept()

        countdown_timer.timeout.connect(update_countdown)
        countdown_timer.start(1000)  # 1秒ごとに更新

        # ダイアログを表示（ブロック）
        msg_box.exec()

        # タイマーを停止
        countdown_timer.stop()


class ProgressDialogHelper:
    """プログレスダイアログのヘルパークラス"""

    @staticmethod
    def create_indeterminate_dialog(
        parent: QWidget,
        title: str,
        message: str,
        min_width: int = 400
    ) -> QProgressDialog:
        """
        不定形プログレスダイアログを作成

        Args:
            parent: 親ウィジェット
            title: タイトル
            message: メッセージ
            min_width: 最小幅

        Returns:
            QProgressDialogオブジェクト
        """
        progress = QProgressDialog(
            message,
            None,  # キャンセルボタンなし
            0,
            0,  # 0 to 0 = 不定形（ビジーインジケーター）
            parent
        )
        progress.setWindowTitle(title)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoReset(False)
        progress.setAutoClose(False)
        progress.setMinimumWidth(min_width)

        # 強制的に表示
        progress.setValue(0)
        progress.show()
        progress.raise_()
        progress.activateWindow()
        QCoreApplication.processEvents()

        return progress

    @staticmethod
    def update_progress_message(progress: QProgressDialog, message: str):
        """
        プログレスダイアログのメッセージを更新

        Args:
            progress: プログレスダイアログ
            message: 新しいメッセージ
        """
        progress.setLabelText(message)
        QCoreApplication.processEvents()

    @staticmethod
    def close_progress(progress: QProgressDialog):
        """
        プログレスダイアログを閉じる

        Args:
            progress: プログレスダイアログ
        """
        progress.close()


class ButtonStyleHelper:
    """ボタンスタイルのヘルパークラス"""

    # 非活性時のスタイル定義
    DISABLED_STYLE = """
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
    """

    # 削除ボタンのスタイル定義
    DELETE_BUTTON_STYLE = """
        QPushButton {
            background-color: #ff6b6b;
            color: white;
        }
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
    """

    @staticmethod
    def apply_disabled_style(button: QPushButton):
        """
        非活性時のスタイルを適用

        Args:
            button: ボタン
        """
        button.setStyleSheet(ButtonStyleHelper.DISABLED_STYLE)

    @staticmethod
    def apply_delete_style(button: QPushButton):
        """
        削除ボタンのスタイルを適用

        Args:
            button: ボタン
        """
        button.setStyleSheet(ButtonStyleHelper.DELETE_BUTTON_STYLE)

    @staticmethod
    def create_large_button(
        text: str,
        min_height: int = 60,
        font_size: int = 14
    ) -> QPushButton:
        """
        大きなボタンを作成

        Args:
            text: ボタンテキスト
            min_height: 最小高さ
            font_size: フォントサイズ

        Returns:
            QPushButtonオブジェクト
        """
        button = QPushButton(text)
        button.setMinimumHeight(min_height)

        font = QFont()
        font.setPointSize(font_size)
        button.setFont(font)

        return button


class FontHelper:
    """フォント作成のヘルパークラス"""

    @staticmethod
    def create_title_font(size: int = 20, bold: bool = True) -> QFont:
        """
        タイトル用フォントを作成

        Args:
            size: フォントサイズ
            bold: 太字にするか

        Returns:
            QFontオブジェクト
        """
        font = QFont()
        font.setPointSize(size)
        font.setBold(bold)
        return font

    @staticmethod
    def create_button_font(size: int = 12) -> QFont:
        """
        ボタン用フォントを作成

        Args:
            size: フォントサイズ

        Returns:
            QFontオブジェクト
        """
        font = QFont()
        font.setPointSize(size)
        return font

    @staticmethod
    def create_status_font(size: int = 14, bold: bool = True) -> QFont:
        """
        ステータス表示用フォントを作成

        Args:
            size: フォントサイズ
            bold: 太字にするか

        Returns:
            QFontオブジェクト
        """
        font = QFont()
        font.setPointSize(size)
        font.setBold(bold)
        return font


class FileOperationHelper:
    """ファイル操作の共通処理ヘルパー"""

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        ファイルサイズを読みやすい形式にフォーマット

        Args:
            size_bytes: サイズ（バイト）

        Returns:
            フォーマットされた文字列
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def format_elapsed_time(seconds: int) -> str:
        """
        経過時間をHH:MM:SS形式にフォーマット

        Args:
            seconds: 経過秒数

        Returns:
            フォーマットされた時間文字列
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# 後方互換性のための関数エイリアス
def show_info_dialog(parent: QWidget, title: str, message: str):
    """情報ダイアログを表示（後方互換性）"""
    DialogHelper.show_info(parent, title, message)


def show_error_dialog(parent: QWidget, title: str, message: str):
    """エラーダイアログを表示（後方互換性）"""
    DialogHelper.show_error(parent, title, message)


def show_question_dialog(
    parent: QWidget,
    title: str,
    message: str,
    default_yes: bool = False
) -> bool:
    """確認ダイアログを表示（後方互換性）"""
    return DialogHelper.show_question(parent, title, message, default_yes)


def create_progress_dialog(
    parent: QWidget,
    title: str,
    message: str
) -> QProgressDialog:
    """プログレスダイアログを作成（後方互換性）"""
    return ProgressDialogHelper.create_indeterminate_dialog(
        parent, title, message
    )
