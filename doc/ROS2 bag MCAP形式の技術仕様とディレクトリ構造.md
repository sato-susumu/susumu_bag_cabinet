# ROS2 bag MCAP形式の技術仕様とディレクトリ構造

**ROS2のrosbag2は、2023年5月のIron Irwini以降、デフォルトストレージ形式としてMCAP（em-cap）を採用しています。**この変更により、従来のSQLite3形式と比較して書き込みスループットが最大200%向上し、データ破損耐性が大幅に改善されました。本レポートでは、MCAP形式の技術仕様、ディレクトリ構造、実装詳細、そして実践的な使用方法について包括的に解説します。

## ディレクトリ構造とその設計思想

### なぜ「ファイル」ではなく「フォルダ」が作られるのか

`ros2 bag record -o my_bag`を実行すると、実際には**ディレクトリ**が作成されます：

```
my_bag/
├── metadata.yaml
└── my_bag_0.mcap
```

この仕組みは、rosbag2の根本的なアーキテクチャ設計に基づいています。**ディレクトリ構造を採用する技術的理由**は以下の通りです：

**プラグインアーキテクチャの実現**: rosbag2は`pluginlib`を使用したストレージプラグインシステムを採用しています。ディレクトリ構造により、異なるストレージ実装（MCAP、SQLite3など）が同じインターフェースで動作可能になります。プラグインは`rosbag2_storage::storage_interfaces::ReadWriteInterface`を実装し、`plugin_description.xml`で登録されます。

**ファイル分割への対応**: 大容量データの記録では、ファイルサイズや記録時間による分割が必要です。`-b`（最大ファイルサイズ）や`-d`（最大記録時間）オプションを使用すると、複数の.mcapファイルが作成されます：

```
my_bag/
├── metadata.yaml
├── my_bag_0.mcap
├── my_bag_1.mcap
└── my_bag_2.mcap
```

**メタデータの集中管理**: metadata.yamlはバッグ全体のカタログとして機能し、全てのストレージファイルを統括します。これにより、データファイルをパースせずにバッグの内容を効率的に検査できます。

**CLI表記の「ファイル」という表現**は、ユーザー体験の簡略化を目的とした**概念的抽象化**です。ROS 1のrosbagが単一の.bagファイルだった歴史的経緯もあり、ユーザーはバッグディレクトリを機能的な単一ユニットとして扱います。技術的には常にディレクトリですが、APIとCLIはこれを原子的な「バッグファイル」として扱います。

### metadata.yamlの構造と役割

metadata.yamlはrosbag2の**中核的インデックスファイル**です。以下は実際の構造例です：

```yaml
rosbag2_bagfile_information:
  version: 9                    # メタデータスキーマバージョン
  storage_identifier: mcap      # 使用するストレージプラグイン
  duration:
    nanoseconds: 33682218527    # 記録総時間
  starting_time:
    nanoseconds_since_epoch: 1740716266541547131
  message_count: 2688           # 総メッセージ数
  
  topics_with_message_count:
    - topic_metadata:
        name: /ultrasound
        type: sensor_msgs/msg/Range
        serialization_format: cdr
        offered_qos_profiles:     # QoS設定（完全保存）
          - history: unknown
            depth: 0
            reliability: reliable
            durability: volatile
        type_description_hash: RIHS01_b42b62562...
      message_count: 2688
  
  compression_format: ""
  compression_mode: ""
  
  relative_file_paths:          # ストレージファイルのリスト
    - my_bag_0.mcap
  
  files:                        # ファイルごとの詳細情報
    - path: my_bag_0.mcap
      starting_time:
        nanoseconds_since_epoch: 1740716266541547131
      duration:
        nanoseconds: 33682218527
      message_count: 2688
  
  ros_distro: "jazzy"
```

**主要機能**：

**発見メカニズム**: rosbag2は`ros2 bag play`実行時に最初にmetadata.yamlを読み込みます。これにより、使用するストレージプラグイン（`storage_identifier`）を決定し、適切なプラグインをロードします。

**トピックカタログ**: 全トピックの型情報、シリアライゼーション形式、QoSプロファイル、メッセージ定義ハッシュを記録します。これにより、再生時に正確な型とQoS設定でトピックを再構築できます。

**分割バッグの統合**: `relative_file_paths`と`files`フィールドにより、複数のストレージファイルを時系列順に統合して再生できます。各ファイルの開始時刻と継続時間が記録されているため、正確なメッセージ順序が保証されます。

**記録時の動作**: metadata.yamlは記録開始時に初期バージョンが作成され、新しいトピックが検出されるたびに更新されます。**重要な点として、最終統計はクリーンシャットダウン時（Ctrl+C）にのみ書き込まれます**。記録中にクラッシュすると、metadata.yamlが不完全または欠損する可能性があります（GitHub issue #395）。

**再生時の動作**: metadata.yamlが存在する場合、リストされたファイルの存在を検証し、型情報とQoSを使用してトピックを正確に復元します。metadata.yamlが欠損した場合、SQLite3バッグは**完全に読み取り不能**になりますが、MCAPファイルは自己完結型のため単体で再生可能です。

## MCAP形式の技術仕様

### ファイル構造の詳細

MCAPはFoxglove Technologies開発のオープンソースコンテナフォーマットで、**append-only（追記専用）設計**と**チャンクベースの組織化**を特徴とします。全体構造は以下の通りです：

```
[Magic Bytes: 0x89 M C A P 0x30 \r \n]
[Header Record]
[Data Section]
  ├── Schema Records (メッセージ定義)
  ├── Channel Records (トピック情報)
  ├── Message Records (単体メッセージ、または)
  └── Chunk Records (圧縮・インデックス化されたメッセージバッチ)
      └── Message Index Records (各チャンクの直後)
[Data End Record]
[Summary Section] (オプション)
  ├── Schema Records (重複)
  ├── Channel Records (重複)
  ├── Chunk Index Records
  ├── Attachment Index Records
  ├── Metadata Index Records
  └── Statistics Record
[Summary Offset Section] (オプション)
[Footer Record]
[Magic Bytes: 0x89 M C A P 0x30 \r \n]
```

**バイナリフォーマットの詳細**：

全てのレコードは統一された構造に従います：`<opcode (1バイト)><length (uint64)><content>`。リトルエンディアンを使用し、タイムスタンプはエポックからのナノ秒（uint64）で表現されます。オペコードは`0x01-0x0F`がMCAPフォーマット用に予約され、`0x80-0xFF`はアプリケーション拡張用です。

**主要レコードタイプ**：

- **Schema (0x03)**: メッセージ型定義（ROS 2では"ros2msg"または"cdr"エンコーディング）
- **Channel (0x04)**: トピックメタデータ（名前、スキーマID、シリアライゼーション形式）
- **Message (0x05)**: 単一のタイムスタンプ付きメッセージ
- **Chunk (0x06)**: 圧縮・インデックス化されたメッセージのバッチ
- **Message Index (0x07)**: チャンク内のメッセージ位置
- **Chunk Index (0x08)**: チャンク位置とメタデータ
- **Statistics (0x0B)**: ファイル全体の統計情報

### チャンクメカニズムとインデックス

**チャンクはMCAPの核心的な組織単位**です。デフォルトで768 KiB（786,432バイト）のサイズで、メッセージをバッチ処理します。

**Chunk Recordの構造**：

```
- message_start_time (8バイト): チャンク内最古のlog_time
- message_end_time (8バイト): チャンク内最新のlog_time
- uncompressed_size (8バイト): 非圧縮時のサイズ
- uncompressed_crc (4バイト): CRC32チェックサム（オプション）
- compression (文字列): "zstd", "lz4", または "" (非圧縮)
- records (可変長): 圧縮または非圧縮のレコードデータ
```

**Message Indexの仕組み**：

各チャンクの直後に、チャンネルごとのMessage Indexレコードが書き込まれます。これにより、チャンク全体を解凍せずに特定メッセージを取得できます：

```
- channel_id (2バイト)
- records: (log_time, offset)のタプル配列
  - log_time (8バイト): メッセージタイムスタンプ
  - offset (8バイト): 非圧縮チャンクデータ内の相対オフセット
```

**Summary SectionのChunk Index**：

ファイル末尾のSummary Sectionには、全チャンクの高速ルックアップ情報が含まれます：

```
- message_start_time / message_end_time: 時間範囲
- chunk_start_offset (8バイト): ファイル内の絶対オフセット
- chunk_length (8バイト): チャンクレコードの総サイズ
- message_index_offsets: channel_id → message index offsetのマップ
- compression: 使用圧縮アルゴリズム
```

この多層インデックス構造により、**O(log n)のチャンク選択とO(1)のメッセージ位置特定**が実現されます。

**インデックス化読み取りの流れ**：

1. ファイル末尾のFooterを読み込み、Summary Section開始位置を取得
2. Summary SectionからChannelレコードを読み込み、トピック名→channel IDをマッピング
3. Chunk Indexレコードから、時間範囲に一致するチャンクを特定
4. 対象チャンクに直接シークし、必要に応じてMessage Indexで精密な位置を特定
5. チャンクを解凍し、目的のメッセージを抽出

### 圧縮アルゴリズムと設定

MCAPは**チャンクレベルでの圧縮**をサポートし、インデックス可能性を維持します。

**Zstandard (zstd)**：
- **圧縮率**: 最高（通常40-60%のサイズ削減）
- **速度**: 中程度の圧縮速度、高速な展開速度
- **レベル**: Fastest、Fast、Default、Slow、Slowest
- **典型的結果**: RGB-Dデータで722.3 MiB → 143.8 MiB（80%削減）

**LZ4**：
- **圧縮率**: 低め（50-70%のサイズ削減）
- **速度**: 非常に高速（数百MB/s）
- **用途**: CPUリソース制約がある環境、リアルタイム記録

**None（非圧縮）**：
- 最速の書き込みパフォーマンス
- 最大のファイルサイズ
- デフォルト設定

**圧縮設定の指定方法**：

YAML設定ファイルを作成：

```yaml
# storage_config.yaml
compression: "Zstd"
compressionLevel: "Fast"
chunkSize: 786432          # デフォルト768 KiB
noChunkCRC: false          # CRC計算を有効化
```

使用例：
```bash
ros2 bag record -s mcap --all --storage-config-file storage_config.yaml
```

**重要な区別**：MCAP pluginの圧縮は**チャンクレベル**で動作し、インデックスを保持します。rosbag2の`--compression-mode file`はファイル全体を圧縮し、インデックスを破壊します。**MCAPの組み込み圧縮を使用することを強く推奨します**。

### SQLite3形式との技術的差異

**構造上の違い**：

| 観点 | MCAP | SQLite3 |
|------|------|---------|
| アーキテクチャ | Append-only、行指向 | トランザクションベース、リレーショナル |
| ファイル構成 | 単一.mcapファイル | .db3 + .db3-wal + .db3-shm |
| スキーマ保存 | ファイル内に埋め込み | 外部依存（ROSワークスペース必要） |
| 組織化 | チャンクベース | テーブルベース |

**パフォーマンス比較（mcap.dev公式ベンチマーク）**：

| 条件 | メッセージサイズ | SQLite3 | MCAP | MCAP優位性 |
|------|----------------|---------|------|-----------|
| デフォルト | 1MiB | ~900 MiB/s | ~1100 MiB/s | +22% |
| デフォルト | 10KiB | ~180 MiB/s | ~250 MiB/s | +39% |
| デフォルト | 100B | ~15 MiB/s | ~45 MiB/s | +200% |
| Resilient | Mixed | ~80 MiB/s | ~220 MiB/s | +175% |

**MCAPの主な利点**：
- 書き込みスループットが一貫して高い（特に小メッセージで顕著）
- Resilientモード（安全設定）でもパフォーマンス低下なし
- 自己完結型のため外部ツール連携が容易
- Append-only設計によりクラッシュ時のデータ損失が最小限

**SQLite3の課題**：
- デフォルトモード（`PRAGMA synchronous=OFF`）は高速だが破損リスク大
- Resilientモード（WAL + NORMAL）は40-60%のパフォーマンス低下
- メッセージスキーマ非保存のため、Foxglove Studioなどで表示困難
- クラッシュ時にデータベース全体が破損する事例多数（GitHub #521）

### MCAPの自己完結性とスキーマ埋め込み

**MessageDefinitionCacheの処理フロー**：

rosbag2_storage_mcapプラグインは、トピック記録時に以下のプロセスでスキーマを埋め込みます：

1. トピックが登録されると`MessageDefinitionCache::get_full_text()`を呼び出し
2. `ament_index_cpp`を使用して、ROSパッケージから.msgまたは.idl定義を検索
3. 正規表現で依存型を抽出（例：`foo_msgs/Bar`、`foo_msgs/msg/Bar`）
4. 再帰的に全依存関係を解決
5. 区切り文字で連結した完全な定義をSchemaレコードに保存
6. SchemaをChannel（トピック）に関連付け

**結果**：.mcapファイルは**完全に自己完結**し、以下が不要になります：
- ROSワークスペース
- メッセージパッケージのインストール
- colcon/amentインデックス

これにより、MCAPファイルは**10年後でも**、オリジナルのメッセージ定義が変更されていても、正確にデコード可能です。

## rosbag2_storage_mcapプラグインの実装

### プラグインアーキテクチャ

rosbag2_storage_mcapは、2022年11月に個別リポジトリからros2/rosbag2メインリポジトリに統合されました。現在のリポジトリ構造：

```
ros2/rosbag2/rosbag2_storage_mcap/
├── src/
│   ├── mcap_storage.cpp              # コアプラグイン実装
│   ├── message_definition_cache.cpp  # スキーマ管理
│   └── mcap_storage_plugin.cpp       # プラグイン登録
├── include/rosbag2_storage_mcap/
│   ├── mcap_storage.hpp
│   └── message_definition_cache.hpp
├── plugin_description.xml            # Pluginlibメタデータ
└── CMakeLists.txt
```

**主要クラス**：

**MCAPStorage**: `rosbag2_storage::storage_interfaces::ReadWriteInterface`を実装。主要メソッド：
- `open()`: MCAPファイルを開く（読み取り/書き込み）
- `create_topic()`: 新しいトピックをスキーマと共に登録
- `write()`: シリアライズされたメッセージを書き込み
- `read_next()`: 次のメッセージを読み取り
- `get_bagfile_size()`: 分割判定用の現在ファイルサイズ取得
- `set_read_order()`: メッセージ順序設定（LogTime、ReverseLogTime、FileOrder）

**プラグイン登録コード**（mcap_storage.cpp）：

```cpp
#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
    rosbag2_storage_plugins::MCAPStorage, 
    rosbag2_storage::storage_interfaces::ReadWriteInterface
)
```

**plugin_description.xml**：

```xml
<library path="rosbag2_storage_mcap">
  <class name="mcap" 
         type="rosbag2_storage_plugins::MCAPStorage" 
         base_class_type="rosbag2_storage::storage_interfaces::ReadWriteInterface">
    <description>MCAP storage plugin for rosbag2</description>
  </class>
</library>
```

### `-s mcap`オプションの効果

`-s`または`--storage`フラグは、使用するストレージプラグインIDを指定します：

```bash
ros2 bag record -s mcap /topic1
```

**プラグイン選択フロー**：

1. `-s mcap`が指定される、またはIron以降ではデフォルトで"mcap"
2. rosbag2_storageが`pluginlib`に"mcap"プラグインを要求
3. Pluginlibが`ament_index`から`plugin_description.xml`を検索
4. 共有ライブラリをロードし、`MCAPStorage`インスタンスを生成
5. 適切なインターフェースメソッドを呼び出し

**自動検出**：再生時（`play`、`info`）は、ファイル拡張子（.mcap vs .db3）とファイル構造から自動的にフォーマットを検出します。強制指定も可能：`ros2 bag info -s mcap path/to/file.mcap`

### プリセットプロファイルと記録オプション

MCAP pluginは**4つのプリセットプロファイル**を提供します：

**1. fastwrite（最高スループット）**：

```yaml
noChunking: true
noSummaryCRC: true
noMessageIndex: true
```

特徴：
- **最速の書き込み**（チャンク化なし）
- メッセージをファイルに直接append
- インデックス生成なし（後処理必要）
- メモリ使用量最小
- **推奨用途**: リソース制約のあるロボット、リアルタイム記録

使用例：
```bash
ros2 bag record -s mcap --all --storage-preset-profile fastwrite
```

後処理：
```bash
ros2 bag convert -i input_bag -o convert.yaml  # 再インデックス化
# またはMCAP CLI: mcap compress input.mcap output.mcap
```

**2. zstd_fast（バランス型圧縮）**：

```yaml
compression: "Zstd"
compressionLevel: "Fast"
noChunkCRC: true
```

特徴：
- 約35%のサイズ削減
- 良好な書き込みスループット
- インデックス可能なまま圧縮
- **推奨用途**: 汎用記録、適度な容量削減

**3. zstd_small（最大圧縮）**：

```yaml
compression: "Zstd"
compressionLevel: "Slowest"
chunkSize: 4194304  # 4 MB
```

特徴：
- 約65%のサイズ削減
- 書き込み時の計算負荷大
- チャンクCRC含む
- **推奨用途**: 長期保管、ポストプロセス

**4. mcap_default（デフォルト）**：

```yaml
compression: "None"
compressionLevel: "Fast"
chunkSize: 786432  # 768 KiB
```

特徴：
- 非圧縮だがチャンク化
- メッセージインデックス有効
- 最適な読み取り効率

### ファイル分割の実装詳細

**サイズベース分割**（`-b`または`--max-bag-size`）：

```bash
ros2 bag record -s mcap -a -b 100000  # 100 KB超過で分割
```

実装：`MCAPStorage::get_bagfile_size()`がMCAPライブラリから累積サイズを取得し、閾値を超えると`should_split_bagfile()`がtrueを返します。MCAPの利点として、ディスクI/Oなしで内部サイズを追跡できます。

最小値：86016バイト（84 KB）

**時間ベース分割**（`-d`または`--max-bag-duration`）：

```bash
ros2 bag record -s mcap -a -d 9000  # 9000秒ごとに分割
```

実装：ファイル開始からの経過時間を追跡し、閾値超過で分割。

**複合条件**：両方指定時は**最初に到達した条件**で分割。手動分割も可能：`~/split_bagfile`サービス呼び出し。

**ファイル命名規則**：

```
my_bag_0.mcap
my_bag_1.mcap
my_bag_2.mcap
...
```

数値接尾辞が順次インクリメント。metadata.yamlの`relative_file_paths`フィールドで全ファイルが管理されます。

**循環ログ機能**（新機能）：

```bash
# 総容量制限（古いファイルを自動削除）
ros2 bag record --max-record-size 10000000

# 総記録時間制限
ros2 bag record --max-record-duration 3600

# 分割回数制限
ros2 bag record --max-splits 10
```

## 再生時の挙動とワークフロー

### ディレクトリ指定vs単体ファイル指定

**ディレクトリからの再生**（標準推奨方法）：

```bash
ros2 bag play my_bag/
```

動作：
1. `my_bag/metadata.yaml`を最初に読み込み
2. `storage_identifier`から使用プラグイン決定（"mcap"）
3. `relative_file_paths`の全ファイルを開く
4. トピックメタデータを使用して正確な型とQoSで再構築
5. 分割バッグの場合、時系列順にメッセージを統合再生

**単体ファイルからの再生**：

```bash
ros2 bag play my_bag/my_bag_0.mcap
```

動作：
1. **metadata.yamlをバイパス**
2. ファイル拡張子/マジックバイトから形式を自動検出
3. ファイル内埋め込みメタデータを読み取り（MCAP機能）
4. **MCAPでは動作**するが、SQLite3 .db3では失敗
5. 分割バッグの場合、指定ファイルのみ再生（他のセグメント無視）

**比較表**：

| 側面 | ディレクトリ再生 | 直接ファイル再生 |
|------|----------------|-----------------|
| メタデータソース | metadata.yaml | ファイル埋め込み |
| 分割バッグサポート | 全ファイル統合 | 指定ファイルのみ |
| SQLite3サポート | ○ | × |
| MCAPサポート | ○ | ○ |
| QoS復元 | 完全 | ファイル依存 |
| 推奨度 | ✓ 標準 | 限定用途 |

### metadata.yamlの影響と重要性

**metadata.yaml存在時**：
- ファイル存在の事前検証
- 分割バッグの正確な時系列統合
- 記録されたQoSプロファイルの適用
- トピックフィルタリングの効率化（データファイル解析不要）
- 明確なエラーメッセージ（ファイル欠損時）

**metadata.yaml欠損時**：
- **SQLite3**: 完全な読み取り不能（GitHub #395で報告された深刻な問題）
- **MCAP**: 単体ファイルとして再生可能（自己完結性のため）
- ROSディストロ情報、カスタムメタデータの損失
- 分割バッグの統合不能

**実例**：50GBのAutowareデータを記録中にクラッシュし、metadata.yamlが破損。SQLite3形式では全データが読み取り不能になったケースが日本語コミュニティで報告されています。MCAPではこの問題が大幅に緩和されます。

### 実践的な使用パターン

**個別分割ファイルの再生**：

```bash
ros2 bag play my_bag/my_bag_0.mcap  # 最初のセグメントのみ
```

**複数バッグの統合再生**：

```bash
ros2 bag play -i bag1/ -i bag2/  # 時間順にマージ
```

**メッセージ順序指定**：

```bash
ros2 bag play --message-order received  # デフォルト（log_time順）
ros2 bag play --message-order sent      # publish_time順
```

**読み取り順序の設定**（rosbag2 Python API）：

```python
from rosbag2_py import ReadOrder

reader.set_read_order(ReadOrder.ReceivedTimestamp)  # log_time順
reader.set_read_order(ReadOrder.PublishedTimestamp) # publish_time順
reader.set_read_order(ReadOrder.FileOrder)          # 最速（インデックス不使用）
```

**FileOrder**はインデックスを使用せず、ファイルに書き込まれた順序で読み取るため最も高速ですが、トピック間の時間順序は保証されません。fastwriteモードで記録した場合はFileOrderのみ利用可能です（警告が表示されます）。

## 日本語コミュニティからの実践知見

### プロダクション環境でのベストプラクティス

**サイバーエージェントの運用例**（ROSCon JP 2024）：

1. **記録フェーズ**: ロボット上で`fastwrite`プロファイル使用
   - 取りこぼし防止を最優先
   - 低CPUオーバーヘッド
   
2. **転送フェーズ**: ネットワーク経由でサーバーに転送

3. **後処理フェーズ**: `ros2 bag convert`で再インデックス化と圧縮
   - zstd_small適用で長期保管用に最適化
   - ストレージコスト削減

**推奨ワークフロー**：

```bash
# ロボット上での記録
ros2 bag record -s mcap --all --storage-preset-profile fastwrite

# サーバー側での最適化
ros2 bag convert -i raw_bag -o convert.yaml
```

convert.yaml：
```yaml
output_bags:
  - uri: optimized_bag
    storage_id: mcap
    storage_config_uri: zstd_small_config.yaml
    all: true
```

### よくある問題と解決策

**問題1: ROS 2 Humbleのrqt_bagがMCAP非対応**

症状：`sqlite3.DatabaseError: file is not a database`エラー

解決策：
- Rolling/Jazzyではすでに対応済み
- Humbleでは代替として：
  - Foxglove Studio使用（ブラウザベース、推奨）
  - PlotJuggler 3.6+使用
  - MCAP CLI: `mcap echo file.mcap /topic`

**問題2: Lz4圧縮でのエラー**

Fixstarsブログで報告：Lz4のdefault/slow設定でエラー発生

推奨：Zstd圧縮を優先使用

**問題3: CRC計算のパフォーマンス影響**

現在の実装ではCRC計算が書き込みスループットに影響します。

トレードオフ：
- データ整合性重視：CRC有効化（`noChunkCRC: false`）
- スループット重視：CRC無効化（`noChunkCRC: true`）

**問題4: metadata.yaml破損時の復旧**

SQLite3では復旧困難ですが、MCAPでは以下が可能：

```bash
# MCAP直接再生（metadata.yaml不要）
ros2 bag play file.mcap

# metadata.yaml再生成（rosbag2 Python API使用）
# カスタムスクリプトが必要
```

### 日本語リソースの推奨

**学習リソース**：
- Qiita: zumax氏の「ROS2コマンドとMCAPを試してみた」- 基本操作
- Fixstarsブログ: rosbag2_storage_mcap使用ガイド - 圧縮比較ベンチマーク
- ROSCon JP 2024: サイバーエージェント吉村氏の発表 - プロダクション運用

**ツール紹介**（日本語記事から）：
- **Foxglove Studio**: ブラウザベース、MCAP完全サポート
- **PlotJuggler**: 3.6+でMCAPサポート
- **MCAP editor**: GUIベースの編集ツール（トピック削除、時間範囲選択、圧縮変更）
- **Kappe**: CUIベースの編集ツール（トピックリネーム、時間トリミング）

## 総合推奨事項

### 用途別の設定ガイド

**リソース制約ロボット（組み込み、バッテリー駆動）**：
```bash
ros2 bag record -s mcap --all \
  --storage-preset-profile fastwrite \
  -b 2000000000  # 2GB分割
```
後でサーバー側で再処理。

**汎用開発・テスト**：
```bash
ros2 bag record -s mcap --all \
  --storage-preset-profile zstd_fast
```
バランスの取れた性能と容量。

**長期アーカイブ**：
```bash
ros2 bag record -s mcap --all \
  --storage-preset-profile zstd_small
```
最大圧縮、CRC有効化。

**デバッグ・短時間記録**：
```bash
ros2 bag record -s mcap /topic1 /topic2
```
デフォルト設定で十分。

### 移行ガイドライン

**既存SQLite3ユーザー向け**：

1. 既存データはSQLite3形式で保持
2. 新規記録はMCAPに切り替え（Iron以降は自動）
3. 重要な履歴データをMCAPに変換：
   ```bash
   ros2 bag convert -i old_bag.db3 -o convert.yaml
   ```
4. 可視化ツールをMCAP対応版に更新
5. 必要時は`--storage-id sqlite3`で明示指定

**新規プロジェクト**：

- デフォルトでMCAP使用（ROS 2 Iron以降）
- 用途に応じたプリセット選択
- 分割サイズは2-4GB推奨
- CIパイプラインに`mcap doctor`統合（整合性チェック）

### 最後に

MCAP形式は、ROS 2のデータロギングにおいて**パフォーマンス、信頼性、相互運用性**の面で大幅な進歩をもたらしました。**Append-only設計**によるクラッシュ耐性、**自己完結型ファイル**による長期保存性、そして**チャンクベースインデックス**による効率的なランダムアクセスは、SQLite3形式の制約を克服する現代的なソリューションです。

rosbag2のディレクトリ構造は、プラグインアーキテクチャと分割バッグサポートを実現するための本質的な設計であり、metadata.yamlは全体を統括する重要なカタログとして機能します。MCAPの自己完結性により、metadata.yaml欠損時でも単体ファイルとして利用可能な点は、実運用での大きな安心材料です。

技術的に正確な理解と適切な設定により、ROS 2開発者はデータロギングの信頼性とパフォーマンスを最大化できます。