# Susumu Bag Cabinet

ROS2 Bagファイル管理アプリケーション - タッチパネル対応のGUIツール

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![ROS2](https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-blue.svg)

## 概要

注意：このリポジトリは生成AIで適当に作ってます。  

Susumu Bag Cabinetは、ROS2のbagファイル（MCAP/DB3形式）を簡単に記録・管理・閲覧できるGUIアプリケーションです。タッチパネル操作を想定した大きなボタンと直感的なインターフェースを提供します。

### 主な特徴

- 🎯 **タッチパネル対応** - 大きな正方形ボタンで簡単操作
- 📦 **簡単記録** - ワンクリックでbag記録開始・停止
- 📊 **自動メタデータ取得** - ファイル情報をバックグラウンドで自動取得


## スクリーンショット

### ホーム画面
![ホーム画面](screenshots/home_screen.png)

3つの大きな正方形ボタンで主要機能にアクセス。

### 記録画面
![記録画面](screenshots/record_screen.png)

- カスタムラベル設定
- リアルタイムの経過時間表示
- ファイルサイズのモニタリング
- 自動ファイル名生成

### 閲覧画面
![閲覧画面](screenshots/browse_screen.png)

- ファイル一覧表示（サイズ、日時、形式、圧縮状態）
- チェックボックスで複数選択
- 圧縮・修復・削除・Foxglove再生

### 設定画面
![設定画面](screenshots/settings_screen.png)

- 保存先フォルダ設定
- ロボット名設定
- ファイル名プレビュー

## 必要要件

### システム要件
- Python 3.8以上
- ROS2 (Humble / Iron / Jazzy)
- Linux (Ubuntu 22.04推奨)

### 必須パッケージ
- PySide6 >= 6.5.0
- PyYAML >= 6.0
- ros2 bag コマンド

### オプション
- Foxglove Studio (bag再生機能を使う場合)

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/susumu_bag_cabinet.git
cd susumu_bag_cabinet
```

### 2. 依存パッケージのインストール

```bash
# Python依存関係
pip install -r requirements.txt

# または開発モードでインストール
pip install -e .
```

### 3. ROS2環境のセットアップ

```bash
source /opt/ros/humble/setup.bash  # または iron, jazzy
```

## 実行方法

```bash
python -m susumu_bag_cabinet.main
```



## 設定ファイル

設定は以下の場所に保存されます:

```
~/.config/susumu_bag_cabinet/config.json
```

**設定内容:**
```json
{
  "bag_folder": "/home/user/ros2_bags",
  "robot_name": "robot1",
  "foxglove_command": "foxglove-studio",
  "filename_include_robot_name": false
}
```

