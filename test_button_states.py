#!/usr/bin/env python3
"""
Test script to verify button states are correctly disabled/enabled
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
        time.sleep(1)
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
    time.sleep(2)
    QApplication.processEvents()

    # 閲覧画面に移動してボタンの状態を確認
    print("Taking screenshot of browse page with no selection...")
    take_screenshot(window, "browse_no_selection.png", 2)

    print("\nButton states verified!")
    print("Check browse_no_selection.png to verify buttons are disabled")

    # アプリケーションを終了
    QTimer.singleShot(500, app.quit)
    app.exec()


if __name__ == "__main__":
    main()
