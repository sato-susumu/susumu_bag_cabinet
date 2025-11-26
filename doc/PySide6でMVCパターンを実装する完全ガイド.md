# PySide6でMVCパターンを実装する完全ガイド

PySide6でロジックと見た目を分離する方法は大きく2つあります。**アプリケーションレベルのMVCパターン**と、**Qt特有のModel/Viewアーキテクチャ**です。本レポートでは両方のアプローチについて、実装例が豊富な日本語・英語リソースを厳選して紹介し、具体的な実装方法とベストプラクティスを解説します。最も重要な発見は、Qtが伝統的なMVCのViewとControllerを統合した独自のModel/View設計を採用している点で、これにより複雑さを減らしながらも強力なデータ分離を実現しています。

## Qtの2つのアーキテクチャパターン

PySide6では用途に応じて2つの設計パターンを使い分けます。**アプリケーション全体の構造にはMVCパターン**を、**リスト・テーブル・ツリーなどのデータ表示にはModel/Viewパターン**を適用するのが一般的です。MVCパターンではModel（データとロジック）、View（UI）、Controller（仲介役）を完全に分離しますが、QtのModel/ViewパターンではViewとControllerが統合され、代わりにDelegateという描画・編集用コンポーネントが追加されています。この設計により、Qtはシンプルさと柔軟性を両立しています。

## 最高品質の日本語リソース

### Qiita: 完全なMVC実装ガイド（★★★★★）

**URL**: https://qiita.com/ker38c/items/e28f7aca6a1c7e34a91b

このQiita記事は日本語リソースの中で最も包括的です。**加算アプリケーションを題材に、Model・View・Controllerの3層を明確に分離した実装**を段階的に解説しています。Qt Designerで作成した.uiファイルをPythonで読み込む方法、シグナルとスロットでMVC間を接続する方法、各層の責任分離の原則が、完全なコードとフォルダ構造とともに示されています。

**フォルダ構成例**:
```
PySide6Sample/
├─ controllers/
│  └─ controller.py     # 入力検証とModel/Viewの調整
├─ models/
│  └─ model.py          # データ保持とビジネスロジック
├─ views/
│  ├─ Addition.ui       # Qt Designerで作成
│  ├─ Ui_Addition.py    # pyside6-uicで変換
│  └─ view.py           # UIの操作とイベント
└─ app.py               # メインアプリケーション
```

**実装の要点**: ModelはQObjectを継承してシグナルでデータ変更を通知し、ViewはGUIの描画とユーザー入力を担当、ControllerはModelとViewの橋渡しをして入力検証を行います。中級〜上級者向けですが、MVCパターンの理解があれば最適な学習教材です。

### はてなブログ: MVCクラス設計の基礎（★★★★☆）

**URL**: https://freedomtsubasa.hatenablog.com/entry/2017/12/07/012724

PyQt5での解説ですが、PySide6にもそのまま適用できる内容です。**MVCパターンの各コンポーネントの責務を明確に定義**し、特に「ModelはControllerやViewにアクセスできない」という重要な設計原則を強調しています。ボタンクリックでラベルを更新する簡単なデモアプリで、クラス間の依存関係を具体的なコードで示しており、初心者〜中級者の入門に最適です。

**設計原則**:
- Model: データの格納とそのデータを用いた処理（独立性を保つ）
- View: Modelのデータを描画
- Controller: Model、Viewに司令を出す
- ControllerとViewは他の2つにアクセス可能だが、Modelは独立

### brian: Qt Designerを使ったUI/ロジック分離（★★★★★）

**URL**: https://brian0111.com/pyside6-qt-designer-gui/

**ToDoリストアプリの実装を通じて、Qt Designerでの画面設計からPythonコードへの連携まで**を画像付きで完全解説しています。QUiLoaderを使った.uiファイルの動的読み込み、findChild()でのウィジェットアクセス、シグナル/スロットでの機能実装が、実用的なコード例とともに示されています。初心者〜中級者向けのステップバイステップガイドで、UI/ロジック分離の実践的な手法を学べます。

**実装パターン**:
```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

# .uiファイルの読み込み
loader = QUiLoader()
ui_file = QFile("todo.ui")
ui_file.open(QFile.ReadOnly)
window = loader.load(ui_file)

# ウィジェットへのアクセスと機能実装
task_input = window.findChild(QLineEdit, "taskInput")
add_button = window.findChild(QPushButton, "addButton")
add_button.clicked.connect(add_task_function)
```

### その他の日本語リソース

- **しんすーブログ - PySide6入門**: https://shinsu-blog.com/python-gui-pyside6-tkinter-kivy/ （初心者向け基礎からQt Designerまで）
- **Zenn - PySide6 入門 001**: https://zenn.dev/m10k1/articles/fbb33e79661050 （シグナル/スロット、レイアウト管理の基本）
- **Taguma CG Lab - UIとロジック分離**: https://cg-lab.mirage-factory.net/2017/11/205/ （設計思想と再利用可能なコンポーネント）

## 最高品質の英語リソース

### Python GUIs: Model/Viewアーキテクチャチュートリアル（★★★★★）

**URL**: https://www.pythonguis.com/tutorials/pyside6-modelview-architecture/

Martin Fitzpatrick氏による**最も実践的で完全なチュートリアル**です。Todoアプリケーションをゼロから構築しながら、QtのModel/Viewアーキテクチャを段階的に解説しています。QAbstractListModelのサブクラス化、data()やrowCount()の実装、Qtロール（DisplayRole、DecorationRole）の使い方、JSON形式でのデータ永続化まで、200行の実行可能なコードとともに提供されています。

**重要な概念**:
- Modelはデータストアとビューの間のインターフェース
- データは任意の構造（Pythonリスト、辞書、データベース）で保存可能
- Viewはモデルがシグナルを発信すると自動的に更新
- `layoutChanged.emit()`と`dataChanged.emit()`でビューに通知

### 公式Qt Documentation: Model/View Programming（★★★★★）

**URL**: https://doc.qt.io/qt-6/model-view-programming.html

QtのModel/Viewアーキテクチャの**公式かつ権威ある完全なリファレンス**です。Model/View vs MVC の違い、QAbstractItemModelインターフェース、モデルインデックスとデータロール、カスタムモデルの作成（読み取り専用と編集可能）、ビュー（QListView、QTableView、QTreeView）、デリゲート、プロキシモデルまで網羅しています。C++の例が多いですが、Pythonにも直接適用できます。

**主要セクション**:
1. The model/view architecture - 理論的基礎
2. Creating New Models - 実装ガイド
3. Using Models and Views - 統合パターン
4. Model Subclassing Reference - 必須の仮想関数

### Stack Overflow: Qt DesignerとMVCデザイン（★★★★☆）

**URL**: https://stackoverflow.com/questions/26698628/mvc-design-with-qt-designer-and-pyqt-pyside

**アプリケーションスケールのMVC設計**について、プロジェクト構造と完全なコード例を含む詳細な回答です。QtのModel/View（ウィジェット用）とアプリケーション全体のMVCの違いを明確にし、ViewがシグナルでModelを監視し、ControllerがModelを操作するパターンを示しています。

**推奨プロジェクト構造**:
```
project/
  mvc_app.py              # メインアプリケーション
  controllers/
    main_ctrl.py          # Controllerクラス
  model/
    model.py              # Modelクラス
  views/
    main_view.py          # Viewクラス
    main_view_ui.py       # Qt Designerから自動生成
  resources/
    main_view.ui          # Qt Designerファイル
```

### GitHub: qt-python-mvc（★★★★☆）

**URL**: https://github.com/tom-a-horrocks/qt-python-mvc

PySide2/6用の**完全なMVCフレームワーク**で、プロパティバインディングアプローチを採用しています。@observableデコレーターを使ったObservableパターン、Model/ControllerのQt非依存設計、Binderクラスでの双方向データバインディングが特徴です。

**ユニークなアプローチ**:
```python
class Model(Observable):
    @property
    def edit_text(self) -> str:
        return self._edit_text
    
    @edit_text.setter
    @observable  # 自動的にシグナルを発信
    def edit_text(self, val: str) -> None:
        self._edit_text = val

# Viewでのバインディング
b = Binder(model)
b.two_way(element1=line_edit.text, 
          element2=Model.edit_text,
          initial_value='Enter text here...')
```

### その他の重要な英語リソース

- **Qt Forum - 最もシンプルなMVC例**: https://forum.qt.io/topic/161479/simplest-mvc-pattern-in-pyside6 （40行のカウンターアプリ）
- **Python Tutorial - PyQt Model/View**: https://www.pythontutorial.net/pyqt/pyqt-model-view/ （初心者向け導入）
- **Cheminformania - 実世界のMVC**: https://www.cheminformania.com/rdkit-gui-browser-with-mvc-using-pyside/ （分子ブラウザアプリの詳細事例）
- **DataCamp - PySide6チュートリアル**: https://www.datacamp.com/tutorial/introduction-to-pyside6-for-building-gui-applications-with-python

## 実装パターン1: アプリケーションレベルMVC

アプリケーション全体の構造を整理する伝統的なMVCパターンです。各コンポーネントは明確な責任を持ち、**シグナル/スロット機構で疎結合を実現**します。

### 完全な実装例

```python
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

# Model: データとビジネスロジック（Qt非依存が理想）
class AppModel(QObject):
    data_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self._data = {'count': 0}
    
    def update_count(self, increment):
        self._data['count'] += increment
        # Viewに変更を通知
        self.data_changed.emit(self._data)
    
    def get_count(self):
        return self._data['count']

# Controller: ユーザーアクションを処理
class AppController:
    def __init__(self, model):
        self.model = model
    
    def handle_increment(self):
        # ビジネスロジックの実行
        self.model.update_count(1)
    
    def handle_decrement(self):
        self.model.update_count(-1)

# View: UI表示のみ
class MainWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.model = model
        self.controller = controller
        
        # UI構築
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.label = QLabel("Count: 0")
        self.inc_btn = QPushButton("Increment")
        self.dec_btn = QPushButton("Decrement")
        
        layout.addWidget(self.label)
        layout.addWidget(self.inc_btn)
        layout.addWidget(self.dec_btn)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # ボタンをControllerに接続
        self.inc_btn.clicked.connect(controller.handle_increment)
        self.dec_btn.clicked.connect(controller.handle_decrement)
        
        # ModelからのデータをViewに反映
        self.model.data_changed.connect(self.update_display)
    
    def update_display(self, data):
        self.label.setText(f"Count: {data['count']}")

# アプリケーション起動
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    model = AppModel()
    controller = AppController(model)
    view = MainWindow(model, controller)
    view.show()
    sys.exit(app.exec())
```

### MVCパターンのベストプラクティス

**責任の分離**を厳密に守ります。Modelはビジネスロジックとデータを持ち、UI要素を一切知りません。ViewはUIの描画とユーザー入力の受付のみを行い、ロジックを含めません。ControllerはModelとViewを調整し、ユーザーアクションを受け取ってModelのメソッドを呼び出します。**通信はシグナル/スロットで行い**、ModelからViewへはシグナルで通知、ViewからControllerへはボタンクリックなどのシグナルを接続します。

## 実装パターン2: Qt Model/Viewアーキテクチャ

QListView、QTableView、QTreeViewなどのデータ表示ウィジェット用の特化型パターンです。**Qtが伝統的MVCのViewとControllerを統合**し、代わりにDelegateで個別アイテムの描画・編集を担当します。

### QtのModel/View vs 伝統的MVC

伝統的MVCでは、Model（データ）、View（表示）、Controller（入力処理）が独立していますが、**QtのModel/Viewでは、ViewとControllerが統合**され、**Delegateという新しいコンポーネントが追加**されています。公式ドキュメントによれば、「ViewとControllerを統合することで、同じ原則に基づくよりシンプルなフレームワークを提供しながら、データの格納方法と表示方法の分離を維持している」とのことです。

**Delegateの役割**: 個別アイテムのカスタム描画、編集ウィジェットの提供、アイテムごとのカスタマイズで、伝統的MVCにはない機能です。デフォルトではQStyledItemDelegateが使用されます。

### QAbstractListModelの実装例

```python
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

class TodoModel(QAbstractListModel):
    def __init__(self, todos=None):
        super().__init__()
        self.todos = todos or []
    
    # 必須メソッド: 行数を返す
    def rowCount(self, parent=QModelIndex()):
        return len(self.todos)
    
    # 必須メソッド: データを返す（ロールに応じて異なるデータ）
    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.todos[index.row()]
            return text
        
        if role == Qt.DecorationRole:
            status, text = self.todos[index.row()]
            if status:
                return QIcon("checkmark.png")
        
        if role == Qt.BackgroundRole:
            status, text = self.todos[index.row()]
            if status:
                return QBrush(QColor("#e0ffe0"))
        
        return None
    
    # データ追加メソッド
    def add_todo(self, text):
        # 行を挿入する前に通知
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.todos.append((False, text))
        self.endInsertRows()  # Viewが自動更新
    
    # データ削除メソッド
    def delete_todo(self, index):
        if 0 <= index < len(self.todos):
            self.beginRemoveRows(QModelIndex(), index, index)
            del self.todos[index]
            self.endRemoveRows()
    
    # データ更新メソッド
    def complete_todo(self, index):
        if 0 <= index < len(self.todos):
            status, text = self.todos[index]
            self.todos[index] = (True, text)
            # 変更を通知
            model_index = self.index(index, 0)
            self.dataChanged.emit(model_index, model_index, [Qt.DecorationRole])

# Viewへの接続
from PySide6.QtWidgets import QListView

view = QListView()
model = TodoModel()
view.setModel(model)  # これだけでViewが自動更新
```

### データロールの活用

QtのModel/Viewの強力な機能の1つが**データロール**です。同じデータを異なる目的で返すことができます：

- **Qt.DisplayRole**: 表示用テキスト
- **Qt.EditRole**: 編集用データ
- **Qt.DecorationRole**: アイコン/画像
- **Qt.ToolTipRole**: ツールチップ
- **Qt.BackgroundRole**: 背景色
- **Qt.ForegroundRole**: 文字色
- **Qt.FontRole**: フォント
- **Qt.TextAlignmentRole**: 配置

```python
def data(self, index, role):
    value = self._data[index.row()]
    
    if role == Qt.DisplayRole:
        return str(value)
    elif role == Qt.BackgroundRole:
        if value < 0:
            return QBrush(Qt.red)  # 負の値は赤背景
    elif role == Qt.ForegroundRole:
        return QBrush(Qt.white)
    elif role == Qt.FontRole:
        font = QFont()
        font.setBold(True)
        return font
    
    return None
```

### QTableViewでの2次元データ

テーブル表示にはQAbstractTableModelを使用します：

```python
from PySide6.QtCore import QAbstractTableModel

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data  # 2次元リスト
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return f"Column {section + 1}"
            else:
                return f"Row {section + 1}"
        return None
    
    # 編集可能にする場合
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

# 使用例
from PySide6.QtWidgets import QTableView

data = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

table_view = QTableView()
model = TableModel(data)
table_view.setModel(model)
table_view.setSortingEnabled(True)  # ソート機能を有効化
```

## UI/ロジック分離のベストプラクティス

### 1. Qt Designerを活用したUI分離

**Qt Designerで.uiファイルを作成**し、ロジックと完全に分離します。2つの方法があります：

**方法A: pyside6-uicでPythonコードに変換**
```bash
pyside6-uic mainwindow.ui -o ui_mainwindow.py
```

```python
from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UIをセットアップ
        self.setup_logic()   # ロジックは別メソッドで
    
    def setup_logic(self):
        # シグナル/スロット接続
        self.pushButton.clicked.connect(self.handle_click)
    
    def handle_click(self):
        # ビジネスロジック
        pass
```

**方法B: QUiLoaderで動的読み込み**
```python
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()
ui_file = QFile("mainwindow.ui")
ui_file.open(QFile.ReadOnly)
window = loader.load(ui_file)
ui_file.close()

# ウィジェットにアクセス
button = window.findChild(QPushButton, "pushButton")
button.clicked.connect(handle_click)
```

### 2. ファイル構成の推奨パターン

```
project_root/
├── models/
│   ├── __init__.py
│   ├── data_model.py        # ビジネスデータとロジック
│   └── table_model.py       # Qt Model/View用モデル
├── views/
│   ├── __init__.py
│   ├── mainwindow.ui        # Qt Designerファイル
│   ├── ui_mainwindow.py     # 自動生成されたUIコード
│   └── main_view.py         # Viewクラス
├── controllers/
│   ├── __init__.py
│   └── main_controller.py   # Controllerロジック
├── resources/
│   ├── icons/
│   └── styles.qss           # スタイルシート
├── main.py                  # エントリーポイント
└── requirements.txt
```

### 3. シグナル/スロットでの疎結合

**カスタムシグナルを定義**してコンポーネント間の結合度を下げます：

```python
from PySide6.QtCore import QObject, Signal

class Model(QObject):
    # カスタムシグナル定義
    value_changed = Signal(int)
    error_occurred = Signal(str)
    
    def update_value(self, new_value):
        if new_value < 0:
            self.error_occurred.emit("Negative value not allowed")
            return
        
        self._value = new_value
        self.value_changed.emit(new_value)

# 接続
model = Model()
model.value_changed.connect(view.update_display)
model.error_occurred.connect(view.show_error)
```

### 4. Modelのテスト可能性

**ModelをQt非依存にすることでユニットテストが容易**になります：

```python
# Pure Pythonのビジネスロジック
class Calculator:
    def add(self, a, b):
        return a + b
    
    def validate_input(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Invalid input")
        return True

# Qtラッパー（必要な場合のみ）
class CalculatorModel(QObject):
    result_ready = Signal(float)
    
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()  # Pure Pythonクラスを使用
    
    def perform_calculation(self, a, b):
        result = self.calculator.add(a, b)
        self.result_ready.emit(result)

# テストコード（Qtなしでテスト可能）
def test_calculator():
    calc = Calculator()
    assert calc.add(2, 3) == 5
```

### 5. 設計原則まとめ

**単一責任の原則**: 各クラスは1つの責任のみを持ちます。Modelはデータ管理、Viewは表示、Controllerは調整です。

**依存性の逆転**: Modelは上位レイヤーに依存せず、ViewとControllerがModelに依存します。Modelは単独でテスト可能です。

**開放閉鎖の原則**: 既存コードを変更せずに機能拡張できる設計にします。新しいViewを追加してもModelは変更不要です。

**インターフェース分離**: 必要なインターフェースのみを公開します。内部実装の詳細は隠蔽します。

## 推奨学習パス

### 初心者向け（PySide6が初めての方）

1. **Zenn記事で基礎概念を理解** (https://zenn.dev/m10k1/articles/fbb33e79661050) - シグナル/スロット、基本ウィジェット
2. **しんすーブログで全体像を把握** (https://shinsu-blog.com/python-gui-pyside6-tkinter-kivy/) - インストールからQt Designerまで
3. **brian記事でQt Designer実践** (https://brian0111.com/pyside6-qt-designer-gui/) - ToDoアプリを実装
4. **Qt Forum のシンプルな例** (https://forum.qt.io/topic/161479/simplest-mvc-pattern-in-pyside6) - 最小限のMVCパターン

### 中級者向け（MVCパターンの実装を学ぶ）

1. **はてなブログでMVC基礎** (https://freedomtsubasa.hatenablog.com/entry/2017/12/07/012724) - クラス設計の原則
2. **Qiita記事で完全実装** (https://qiita.com/ker38c/items/e28f7aca6a1c7e34a91b) - 加算アプリの3層分離
3. **Stack Overflowのアーキテクチャガイド** (https://stackoverflow.com/questions/26698628/mvc-design-with-qt-designer-and-pyqt-pyside) - プロジェクト構造
4. **Python GUIs チュートリアル** (https://www.pythonguis.com/tutorials/pyside6-modelview-architecture/) - Model/View実装

### 上級者向け（高度なパターンと実践）

1. **公式Qt Documentation熟読** (https://doc.qt.io/qt-6/model-view-programming.html) - 完全なリファレンス
2. **GitHub qt-python-mvc研究** (https://github.com/tom-a-horrocks/qt-python-mvc) - 高度なバインディングパターン
3. **Cheminformania事例研究** (https://www.cheminformania.com/rdkit-gui-browser-with-mvc-using-pyside/) - 実世界アプリケーション
4. **カスタムDelegate実装**: 独自の描画・編集ロジックを持つデリゲートの作成

### 言語別リソース優先度

**日本語で学ぶなら**:
1. Qiita記事（完全なMVC実装）
2. brian記事（Qt Designerの実践）
3. はてなブログ（MVCの基本）

**英語で学ぶなら**:
1. Python GUIs（最も実践的）
2. 公式Qt Documentation（最も権威的）
3. GitHub qt-python-mvc（最も高度）

## 実装時のよくある落とし穴と解決策

### beginInsertRows/endInsertRowsの忘れ

**問題**: データを追加してもViewが更新されない

**解決策**: 構造変更時は必ずbegin/endメソッドを呼ぶ
```python
# 誤り
self.todos.append(new_item)

# 正しい
self.beginInsertRows(QModelIndex(), len(self.todos), len(self.todos))
self.todos.append(new_item)
self.endInsertRows()
```

### dataChangedシグナルの発信忘れ

**問題**: データを更新してもViewに反映されない

**解決策**: setData()内で必ずdataChangedを発信
```python
def setData(self, index, value, role):
    if role == Qt.EditRole:
        self._data[index.row()] = value
        self.dataChanged.emit(index, index, [role])  # 必須
        return True
    return False
```

### ModelにUI要素を含める

**問題**: Modelがテストしづらく再利用できない

**解決策**: ModelはQt非依存のPure Pythonクラスにし、必要ならQObjectでラップ

### View内にビジネスロジック

**問題**: ロジックがView内に散在し保守性が低下

**解決策**: ロジックはすべてModelかControllerに移動し、Viewは表示と接続のみ

## 結論

PySide6でロジックと見た目を分離する方法には、**アプリケーション全体を整理するMVCパターン**と、**データ表示に特化したQt Model/Viewパターン**の2つがあります。本調査で発見した日本語・英語の優良リソースを活用すれば、初心者から上級者まで段階的に学習できます。

**即座に始めるなら**: Qiita記事 (https://qiita.com/ker38c/items/e28f7aca6a1c7e34a91b) と Python GUIs (https://www.pythonguis.com/tutorials/pyside6-modelview-architecture/) を並行して読み、実際にコードを動かしてみてください。Qt Designerで.uiファイルを作成し、シグナル/スロットで接続し、ModelにQObjectを継承させてシグナルで通知する、というパターンを体得すれば、保守性の高いPySide6アプリケーションを構築できます。

**重要な原則**: Modelはビジネスロジックとデータのみを持ち、UI要素を知らない。ViewはUIの表示と入力受付のみを行う。ControllerまたはQt Model/Viewがこれらを調整する。シグナル/スロットで疎結合を保つ。これらを守ることで、テストしやすく、再利用可能で、拡張しやすいアーキテクチャを実現できます。