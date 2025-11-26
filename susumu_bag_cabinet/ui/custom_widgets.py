"""
カスタムウィジェット
継承ベースで再利用可能なUIコンポーネントを提供
"""

from PySide6.QtWidgets import QPushButton, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class LargeButton(QPushButton):
    """
    大きなボタンウィジェット
    タッチパネルに最適化された大きなボタン
    """

    def __init__(
        self,
        text: str,
        min_height: int = 60,
        font_size: int = 14,
        parent=None
    ):
        """
        初期化

        Args:
            text: ボタンテキスト
            min_height: 最小高さ
            font_size: フォントサイズ
            parent: 親ウィジェット
        """
        super().__init__(text, parent)

        # サイズ設定
        self.setMinimumHeight(min_height)

        # フォント設定
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)

        # 非活性時のスタイル
        self.setStyleSheet("""
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)


class SquareButton(QPushButton):
    """
    正方形ボタンウィジェット
    ホームページで使用される大きな正方形ボタン
    """

    def __init__(
        self,
        text: str,
        size: int = 200,
        font_size: int = 16,
        parent=None
    ):
        """
        初期化

        Args:
            text: ボタンテキスト
            size: ボタンのサイズ（幅と高さ）
            font_size: フォントサイズ
            parent: 親ウィジェット
        """
        super().__init__(text, parent)

        # サイズ設定
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)

        # フォント設定
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(True)
        self.setFont(font)


class DeleteButton(LargeButton):
    """
    削除ボタンウィジェット
    赤色の警告スタイルを持つボタン
    """

    def __init__(
        self,
        text: str = "削除",
        min_height: int = 60,
        font_size: int = 14,
        parent=None
    ):
        """
        初期化

        Args:
            text: ボタンテキスト
            min_height: 最小高さ
            font_size: フォントサイズ
            parent: 親ウィジェット
        """
        super().__init__(text, min_height, font_size, parent)

        # 削除ボタン専用のスタイル
        self.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)


class CountdownDialog(QMessageBox):
    """
    カウントダウン付き自動クローズダイアログ
    指定秒数後に自動的に閉じる情報ダイアログ
    """

    def __init__(
        self,
        title: str,
        message: str,
        countdown_seconds: int = 3,
        parent=None
    ):
        """
        初期化

        Args:
            title: ダイアログタイトル
            message: メッセージ
            countdown_seconds: カウントダウン秒数
            parent: 親ウィジェット
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Icon.Information)

        # メッセージとカウントダウンを保存
        self.base_message = message
        self.countdown = countdown_seconds

        # 初期メッセージを設定
        self._update_message()

        # カウントダウンタイマーを作成
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._on_countdown)

    def _update_message(self):
        """メッセージを更新"""
        self.setText(f"{self.base_message}\n\n({self.countdown}秒後に自動的に閉じます)")

    def _on_countdown(self):
        """カウントダウン処理"""
        self.countdown -= 1
        if self.countdown > 0:
            self._update_message()
        else:
            self.countdown_timer.stop()
            self.accept()

    def show_with_countdown(self):
        """カウントダウンを開始してダイアログを表示"""
        self.countdown_timer.start(1000)  # 1秒ごとに更新
        self.exec()
        self.countdown_timer.stop()


class IndeterminateProgressDialog(QProgressDialog):
    """
    不定形プログレスダイアログ
    パーセント表示なしの円形インジケーター
    """

    def __init__(
        self,
        title: str,
        message: str,
        min_width: int = 400,
        parent=None
    ):
        """
        初期化

        Args:
            title: ダイアログタイトル
            message: メッセージ
            min_width: 最小幅
            parent: 親ウィジェット
        """
        super().__init__(
            message,
            None,  # キャンセルボタンなし
            0,
            0,  # 0 to 0 = 不定形（ビジーインジケーター）
            parent
        )

        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumDuration(0)
        self.setAutoReset(False)
        self.setAutoClose(False)
        self.setMinimumWidth(min_width)

    def show_and_raise(self):
        """ダイアログを表示して前面に持ってくる"""
        self.setValue(0)
        self.show()
        self.raise_()
        self.activateWindow()
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def update_message(self, message: str):
        """
        メッセージを更新

        Args:
            message: 新しいメッセージ
        """
        self.setLabelText(message)
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()


class TitleLabel(QPushButton):
    """
    タイトルラベル
    ページタイトル用の大きな太字ラベル

    Note: QPushButtonを継承していますが、ラベルとして使用
    （QLabel継承でも可能ですが、既存コードとの互換性のため）
    """

    def __init__(
        self,
        text: str,
        font_size: int = 20,
        bold: bool = True,
        parent=None
    ):
        """
        初期化

        Args:
            text: タイトルテキスト
            font_size: フォントサイズ
            bold: 太字にするか
            parent: 親ウィジェット
        """
        super().__init__(text, parent)

        # フォント設定
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        self.setFont(font)

        # ボタンとして動作しないようにする
        self.setEnabled(False)
        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                text-align: left;
                padding: 0px;
            }
        """)
