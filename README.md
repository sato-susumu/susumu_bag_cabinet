# Susumu Bag Cabinet

ROS2 Bag ファイル管理アプリケーション

## 概要

Susumu Bag Cabinet は、ROS2 の bag ファイル（MCAP形式）を簡単に記録・管理・閲覧できるGUIアプリケーションです。タッチパネル操作を想定した大きなボタンと直感的なインターフェースを提供します。

## 機能

### 🟥 記録する
- ros2 bag record を使った簡単な記録開始/停止
- カスタムラベルの設定
- リアルタイムでの経過時間とファイルサイズ表示
- 自動ファイル名生成（YYYYMMDD_HHMMSS_<ラベル>.mcap）

### 🟦 記録をみる
- bag ファイルの一覧表示
- ファイル情報の自動取得（サイズ、記録開始日時、形式、圧縮状態、整合性）
- バックグラウンドでのメタデータ取得
- Foxglove Studio での再生
- 複数ファイルの一括操作（選択/全選択）

### ⚙ 設定
- 保存先フォルダの変更
- ロボット名の設定
- ファイル名へのロボット名追加オプション
- Foxglove Studio コマンドの設定

## 必要要件

- Python 3.8 以上
- PySide6
- ROS2 (bag コマンドが必要)
- Foxglove Studio (再生機能を使う場合)

## インストール

```bash
# リポジトリをクローン
git clone <repository_url>
cd susumu_bag_cabinet

# 依存パッケージをインストール
pip install -r requirements.txt

# または開発モードでインストール
pip install -e .
```

## 実行方法

```bash
# 直接実行
python -m susumu_bag_cabinet.main

# またはインストール後
susumu-bag-cabinet
```

## 使い方

### 初回起動時
1. アプリケーションを起動すると、ホーム画面が表示されます
2. 「設定をひらく」から保存先フォルダを設定してください（デフォルト: ~/ros2_bags）

### 記録する
1. ホーム画面で「記録する」をクリック
2. 必要に応じてラベルを入力
3. 「記録開始」をクリック
4. 記録を終了するには「記録停止」をクリック

### 記録をみる
1. ホーム画面で「記録をみる」をクリック
2. bag ファイルの一覧が表示されます
3. チェックボックスで操作したいファイルを選択
4. 「Foxgloveで再生」で選択したファイル（1つのみ）を再生

### 設定
1. ホーム画面で「設定をひらく」をクリック
2. 各種設定を変更
3. 「保存してホームへ」で設定を保存

## ファイル構成

```
susumu_bag_cabinet/
├── susumu_bag_cabinet/
│   ├── __init__.py
│   ├── main.py              # エントリーポイント
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # メインウィンドウ
│   │   ├── home_page.py     # ホーム画面
│   │   ├── record_page.py   # 記録画面
│   │   ├── browse_page.py   # 閲覧画面
│   │   └── settings_page.py # 設定画面
│   ├── workers/
│   │   ├── __init__.py
│   │   └── bag_scanner.py   # バックグラウンドスキャナー
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # 設定管理
│       └── bag_utils.py      # bag ファイル操作
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

## 設定ファイル

設定は `~/.config/susumu_bag_cabinet/config.json` に保存されます。

## 注意事項

- 記録中はアプリケーションを閉じないでください（確認ダイアログが表示されます）
- bag ファイルの整合性チェックには時間がかかる場合があります
- Foxglove Studio で再生するには、事前に Foxglove Studio をインストールしておく必要があります

## ライセンス

MIT License

## 開発

### テスト実行

```bash
# アプリケーションのテスト起動
python -m susumu_bag_cabinet.main
```

### 今後の拡張予定

- bag ファイルの圧縮機能
- bag ファイルの修復機能
- トピック選択記録
- 複数ファイルの結合

## トラブルシューティング

### ros2 コマンドが見つからない
ROS2 環境が正しくセットアップされているか確認してください：
```bash
source /opt/ros/<ros_distro>/setup.bash
```

### Foxglove Studio が起動しない
設定画面で正しいコマンドが設定されているか確認してください。デフォルトは `foxglove-studio` です。