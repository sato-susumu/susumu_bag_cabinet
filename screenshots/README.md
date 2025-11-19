# スクリーンショット

このディレクトリには、アプリケーションの主要画面のスクリーンショットを配置します。

## 必要なスクリーンショット

以下のスクリーンショットを撮影してください:

### 1. ホーム画面 (`home_screen.png`)
- 3つの正方形ボタンが表示されている状態
- 推奨サイズ: 1000x700以上

**撮影方法:**
```bash
# アプリケーションを起動
python -m susumu_bag_cabinet.main

# ホーム画面が表示されたらスクリーンショットを撮影
scrot -s screenshots/home_screen.png
# または
gnome-screenshot -a -f screenshots/home_screen.png
```

### 2. 記録画面 (`record_screen.png`)
- 「記録する」ボタンをクリックした後の画面
- ラベル入力欄やステータス表示が見える状態

### 3. 閲覧画面 (`browse_screen.png`)
- 「記録をみる」ボタンをクリックした後の画面
- ファイル一覧テーブルが表示されている状態
- いくつかのファイルにチェックが入っている状態が望ましい

### 4. 設定画面 (`settings_screen.png`)
- 「設定をひらく」ボタンをクリックした後の画面
- 各種設定項目が表示されている状態

## 撮影ツール

### Linux
```bash
# Scrot (推奨)
scrot -s <filename>

# GNOME Screenshot
gnome-screenshot -a -f <filename>

# ImageMagick
import <filename>
```

### 撮影後

スクリーンショットを撮影したら、このディレクトリに以下の名前で保存してください:
- `home_screen.png`
- `record_screen.png`
- `browse_screen.png`
- `settings_screen.png`

画像サイズは自動的にGitHubで適切に表示されます。
