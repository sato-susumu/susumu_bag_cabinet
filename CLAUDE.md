# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Susumu Bag CabinetはROS2のbagファイル（MCAP/DB3形式）を管理するタッチパネル対応のGUIアプリケーションです。PySide6（Qt for Python）を使用し、ロボット開発者がbagファイルの記録・閲覧・管理を直感的に行えるように設計されています。

## アーキテクチャ

### UI構造（QStackedWidgetベース）

アプリケーションは`MainWindow`が`QStackedWidget`を使って4つのページを管理しています：

1. **HomePage** (`ui/home_page.py`) - 3つの正方形ボタン（記録する、記録をみる、設定をひらく）
2. **RecordPage** (`ui/record_page.py`) - ROS2 bag記録の開始/停止、リアルタイムステータス表示
3. **BrowsePage** (`ui/browse_page.py`) - bagファイル一覧、圧縮/修復/削除/Foxglove再生機能
4. **SettingsPage** (`ui/settings_page.py`) - 保存先フォルダ、ロボット名などの設定

各ページは`Signal`を使ってページ遷移を通知し、`MainWindow`が`QStackedWidget.setCurrentIndex()`でページを切り替えます。

### バックグラウンド処理

**BagScanner** (`workers/bag_scanner.py`):
- `QThread`を継承したワーカークラス
- bagファイルのメタデータ（サイズ、日時、圧縮状態、整合性など）をバックグラウンドで取得
- UIスレッドをブロックせずに重い`ros2 bag info`コマンドを実行
- `Signal`でUIに進捗と結果を通知

### 設定管理

**Config** (`utils/config.py`):
- `~/.config/susumu_bag_cabinet/config.json`にJSON形式で設定を保存
- シングルトンパターンで全ページから共有される設定にアクセス

### ROS2 bag操作

**bag_utils.py**: メタデータ取得、MCAP圧縮検出（バイナリヘッダー検査）
**bag_operations.py**: 圧縮・修復機能（`ros2 bag convert`を使用、YAMLコンフィグファイル経由）

## 重要な実装パターン

### 非活性ボタンのスタイル

ファイル選択が必要な操作ボタンは、選択がない場合に非活性化され、グレーアウト表示されます：

```python
button.setStyleSheet("""
    QPushButton:disabled {
        background-color: #e0e0e0;
        color: #9e9e9e;
    }
""")
```

### プログレスダイアログ（不定形）

長時間処理（圧縮・修復・削除）では、パーセント表示ではなく円形インジケーターを使用：

```python
progress = QProgressDialog("処理中...", None, 0, 0, self)  # 0 to 0 = indeterminate
progress.setAutoReset(False)
progress.setAutoClose(False)
```

### 自動閉じカウントダウンダイアログ

記録完了や設定保存時には、3秒のカウントダウン後に自動的に閉じるダイアログを表示：

```python
def _show_completion_dialog(self):
    msg_box = QMessageBox(self)
    countdown = 3
    countdown_timer = QTimer()
    # カウントダウンロジック...
```

### Foxglove Studio起動

bagファイルを直接Foxgloveで開きます：
- MCAPファイル: `foxglove-studio /path/to/file.mcap`
- ディレクトリ形式bag: 内部の`*_0.mcap`ファイルを検索して渡す
- 圧縮ファイル（`.mcap.zstd`）は検出してエラーメッセージを表示

### テーブル行クリック選択

`BrowsePage`のテーブルでは、行のどこをクリックしてもチェックボックスがトグルされます（タッチパネル対応）：

```python
self.table.cellClicked.connect(self._on_table_cell_clicked)

def _on_table_cell_clicked(self, row, column):
    checkbox.setChecked(not checkbox.isChecked())
```

## 開発コマンド

### アプリケーション起動
```bash
# ROS2環境のセットアップが必要
source /opt/ros/humble/setup.bash

# アプリケーション起動
python -m susumu_bag_cabinet.main
```

### 依存関係のインストール
```bash
pip install -r requirements.txt
# または開発モード
pip install -e .
```

### テスト実行
```bash
# 基本コンポーネントテスト
python test_basic.py

# 閲覧機能テスト
python test_browse.py

# GUIテスト
python test_gui.py
```

### スクリーンショット撮影
```bash
python take_screenshots.py
```

## UIデザイン原則

1. **タッチパネル最適化**: ボタンは大きく（記録ボタンは60px高、ホームボタンは200x200px正方形）
2. **日本語UI**: すべてのラベルとメッセージは日本語
3. **視覚的フィードバック**: 非活性ボタンは明確にグレーアウト、記録中は赤色表示
4. **自動化**: カウントダウン後の自動クローズ、バックグラウンドスキャンで待ち時間を削減

## ファイル名生成ルール

記録開始時にファイル名を生成（プレビューなし）：
```
YYYYMMDD_HHMMSS_<ラベル>.mcap
例: 20251119_143025_廊下テスト.mcap
```

## 注意事項

- **ROS2依存**: `ros2 bag`コマンドが必須（record, info, convert）
- **圧縮形式**: Zstdのみサポート（LZ4プラグインは未インストール環境が多い）
- **MCAP検出**: バイナリヘッダー（magic number）で圧縮形式を判定
- **ファイル名とディレクトリ**: `.mcap`拡張子のディレクトリも存在するため、`Path.is_file()`と`Path.is_dir()`の両方をチェック
