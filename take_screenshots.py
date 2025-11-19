#!/usr/bin/env python3
"""
自動的にアプリケーションの各画面のスクリーンショットを撮影するスクリプト
"""

import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from susumu_bag_cabinet.ui.main_window import MainWindow


def take_screenshot(window, filename, page_index=None):
    """ウィンドウのスクリーンショットを撮影"""
    if page_index is not None:
        window.stacked_widget.setCurrentIndex(page_index)
        # ページ切り替え後の描画を待つ
        QApplication.processEvents()
        time.sleep(0.5)
        QApplication.processEvents()

    # スクリーンショットを撮影
    pixmap = window.grab()
    output_path = Path(__file__).parent / "screenshots" / filename
    output_path.parent.mkdir(exist_ok=True)
    pixmap.save(str(output_path))
    print(f"Saved: {output_path}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # ウィンドウが完全に表示されるまで待つ
    QApplication.processEvents()
    time.sleep(1)
    QApplication.processEvents()

    # 各画面のスクリーンショットを撮影
    screenshots = [
        (0, "home_screen.png"),      # ホーム画面
        (1, "record_screen.png"),    # 記録画面
        (2, "browse_screen.png"),    # 閲覧画面
        (3, "settings_screen.png"),  # 設定画面
    ]

    for page_index, filename in screenshots:
        take_screenshot(window, filename, page_index)
        time.sleep(0.5)

    print("\nAll screenshots taken successfully!")
    print("Screenshots saved to: screenshots/")

    # アプリケーションを終了
    QTimer.singleShot(500, app.quit)
    app.exec()


if __name__ == "__main__":
    main()
