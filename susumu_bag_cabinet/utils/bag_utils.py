"""
Utility functions for working with ROS2 bag files.
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def detect_mcap_compression(mcap_path: str) -> str:
    """
    Detect compression format of an MCAP file by reading its header.

    Args:
        mcap_path: Path to the MCAP file

    Returns:
        Compression format string
    """
    try:
        with open(mcap_path, 'rb') as f:
            # 最初の1KBを読み込んで圧縮マーカーを確認
            header = f.read(1024)

            # 一般的な圧縮シグネチャをチェック
            # LZ4マジックナンバー: 0x184D2204
            if b'\x04\x22\x4D\x18' in header:
                return "圧縮(LZ4)"

            # Zstdマジックナンバー: 0xFD2FB528
            if b'\x28\xB5\x2F\xFD' in header or b'zstd' in header.lower():
                return "圧縮(Zstd)"

            # チャンク圧縮を確認するためにさらにデータを読み込む
            f.seek(0)
            data = f.read(8192)

            # MCAP形式の圧縮フィールド指示子を探す
            if b'lz4' in data.lower():
                return "圧縮(LZ4)"
            if b'zstd' in data.lower():
                return "圧縮(Zstd)"

        return "未圧縮"
    except Exception:
        return "未チェック"


def get_bag_info(bag_path: str) -> Dict[str, Any]:
    """
    Get information about a bag file using ros2 bag info.

    Args:
        bag_path: Path to the bag file or directory

    Returns:
        Dictionary containing bag information
    """
    result = {
        "path": bag_path,
        "size": 0,
        "format": "Unknown",
        "start_time": None,
        "duration": None,
        "compression": "未チェック",
        "is_valid": "未チェック",
    }

    # ファイル/ディレクトリのサイズを取得
    path_obj = Path(bag_path)
    if path_obj.exists():
        if path_obj.is_file():
            result["size"] = path_obj.stat().st_size
        elif path_obj.is_dir():
            result["size"] = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())

    # 形式を検出（MCAPのみ）
    if '.mcap' in bag_path:
        # .mcap, .mcap.zstd, .mcap.lz4 などを全て認識
        result["format"] = "MCAP"
    elif path_obj.is_dir():
        # ディレクトリ内のファイルを確認
        has_metadata = (path_obj / 'metadata.yaml').exists()
        mcap_files = [f for f in path_obj.iterdir()
                      if f.is_file() and '.mcap' in f.name]

        if has_metadata or mcap_files:
            result["format"] = "MCAP"

    # ros2 bag infoを使用してメタデータを取得
    try:
        cmd = ['ros2', 'bag', 'info', bag_path]
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if process.returncode == 0:
            output = process.stdout
            result["is_valid"] = "OK"

            # 開始時刻を解析
            time_match = re.search(r'Start:\s+([^\n]+)', output)
            if time_match:
                time_str = time_match.group(1).strip()
                try:
                    # タイムスタンプを解析
                    # 形式: "Jan 1 2025 12:34:56.789 (1234567890.123)"
                    # 括弧内のunixタイムスタンプを抽出（利用可能な場合）
                    unix_match = re.search(r'\((\d+\.\d+)\)', time_str)
                    if unix_match:
                        timestamp = float(unix_match.group(1))
                        result["start_time"] = datetime.fromtimestamp(timestamp)
                    else:
                        # 人間が読める形式を解析
                        # これはフォールバックで、すべての形式で機能するとは限らない
                        result["start_time"] = time_str
                except Exception:
                    result["start_time"] = time_str

            # 記録時間（duration）を解析
            duration_match = re.search(r'Duration:\s+([^\n]+)', output)
            if duration_match:
                duration_str = duration_match.group(1).strip()
                try:
                    # 形式: "12.345s" or "1m23.456s" など
                    result["duration"] = duration_str
                except Exception:
                    result["duration"] = duration_str

            # 圧縮情報を確認（ros2 bag infoは常に表示するとは限らない）
            if 'compression' in output.lower():
                if 'lz4' in output.lower():
                    result["compression"] = "圧縮(LZ4)"
                elif 'zstd' in output.lower():
                    result["compression"] = "圧縮(Zstd)"
                else:
                    result["compression"] = "未圧縮"
        else:
            result["is_valid"] = "NG"

    except subprocess.TimeoutExpired:
        result["is_valid"] = "タイムアウト"
    except FileNotFoundError:
        result["is_valid"] = "ros2コマンド未検出"
    except Exception as e:
        result["is_valid"] = f"エラー: {str(e)}"

    # 圧縮が未判定でMCAPファイルの場合、直接確認
    if result["compression"] == "未チェック" and result["format"] == "MCAP":
        # 実際のMCAPファイルパスを見つける
        mcap_file = None
        if path_obj.is_file() and '.mcap' in bag_path:
            mcap_file = bag_path
        elif path_obj.is_dir():
            # .mcap または .mcap.* のファイルを検索
            mcap_files = [f for f in path_obj.iterdir()
                          if f.is_file() and '.mcap' in f.name]
            if mcap_files:
                mcap_files.sort()
                mcap_file = str(mcap_files[0])

        if mcap_file:
            # ファイル名から圧縮形式を判定
            if mcap_file.endswith('.mcap.zstd') or mcap_file.endswith('.zstd'):
                result["compression"] = "圧縮(Zstd)"
            elif mcap_file.endswith('.mcap.lz4') or mcap_file.endswith('.lz4'):
                result["compression"] = "圧縮(LZ4)"
            elif mcap_file.endswith('.mcap'):
                # 拡張子が.mcapのみの場合、中身をチェック
                result["compression"] = detect_mcap_compression(mcap_file)
            else:
                # その他の圧縮形式
                result["compression"] = "圧縮"

    return result


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(duration_str: Optional[str]) -> str:
    """
    Format duration in human-readable Japanese format.

    Args:
        duration_str: Duration string from ros2 bag info (e.g., "12.345s", "1m23.456s")

    Returns:
        Human-readable duration string in Japanese
    """
    if not duration_str:
        return "-"

    try:
        # Parse duration string
        # Formats: "12.345s", "1m23.456s", "1h2m3.456s"
        total_seconds = 0.0

        # Extract hours if present
        hours_match = re.search(r'(\d+)h', duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600

        # Extract minutes if present
        minutes_match = re.search(r'(\d+)m', duration_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60

        # Extract seconds (always present)
        seconds_match = re.search(r'([\d.]+)s', duration_str)
        if seconds_match:
            total_seconds += float(seconds_match.group(1))

        # Format based on duration
        if total_seconds < 1:
            # Less than 1 second: show milliseconds
            return f"{total_seconds * 1000:.0f}ミリ秒"
        elif total_seconds < 60:
            # Less than 1 minute: show seconds
            return f"{total_seconds:.1f}秒"
        elif total_seconds < 3600:
            # Less than 1 hour: show minutes and seconds
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            return f"{minutes}分{seconds:.0f}秒"
        else:
            # 1 hour or more: show hours, minutes, and seconds
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60
            if seconds > 0:
                return f"{hours}時間{minutes}分{seconds:.0f}秒"
            elif minutes > 0:
                return f"{hours}時間{minutes}分"
            else:
                return f"{hours}時間"
    except Exception:
        # If parsing fails, return original string
        return duration_str


def generate_folder_name(label: str = "", robot_name: str = "", include_robot: bool = False) -> str:
    """
    Generate a folder name for a new bag recording (without .mcap extension).

    Args:
        label: Optional label to include in folder name
        robot_name: Robot name (used if include_robot is True)
        include_robot: Whether to include robot name in folder name

    Returns:
        Generated folder name (without .mcap extension)
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    parts = []
    if include_robot and robot_name:
        parts.append(robot_name)
    parts.append(timestamp)
    if label:
        parts.append(label)

    return "_".join(parts)


def scan_bag_folder(folder_path: str) -> list:
    """
    Scan a folder recursively for MCAP bag files.

    Args:
        folder_path: Path to the folder to scan

    Returns:
        List of bag file/directory paths (sorted by modification time, newest first)
    """
    folder = Path(folder_path)
    if not folder.exists():
        return []

    bag_files = []
    seen = set()  # 重複を避けるため

    # 方法1: すべての.mcapファイルを再帰的に検索
    for p in folder.rglob('*.mcap'):
        if p.is_file():
            # これがROS2 bagディレクトリの一部かどうか確認
            parent_dir = p.parent
            if (parent_dir / 'metadata.yaml').exists():
                # これはROS2 bagディレクトリ - ディレクトリ自体を追加
                dir_path = str(parent_dir)
                if dir_path not in seen:
                    bag_files.append(dir_path)
                    seen.add(dir_path)
            else:
                # スタンドアロンMCAPファイル
                file_path = str(p)
                if file_path not in seen:
                    bag_files.append(file_path)
                    seen.add(file_path)

    # 方法2: metadata.yamlを含むすべてのディレクトリを検索
    # これにより、.mcap拡張子のないROS2 bagディレクトリ（圧縮後など）も検出される
    for metadata_file in folder.rglob('metadata.yaml'):
        if metadata_file.is_file():
            bag_dir = metadata_file.parent
            dir_path = str(bag_dir)
            if dir_path not in seen:
                # このディレクトリ内に.mcapファイルがあるか確認
                # （.mcap.zstdのような圧縮ファイルでもOK）
                has_mcap_files = any(
                    f.suffix == '.mcap' or '.mcap' in f.name
                    for f in bag_dir.iterdir()
                    if f.is_file()
                )
                if has_mcap_files:
                    bag_files.append(dir_path)
                    seen.add(dir_path)

    return sorted(bag_files, key=lambda x: Path(x).stat().st_mtime, reverse=True)
