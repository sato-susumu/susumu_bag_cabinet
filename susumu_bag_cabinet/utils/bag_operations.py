"""
Bag file operations (compression, repair, etc.)
"""

import subprocess
from pathlib import Path
from typing import Optional, Callable


def repair_bag(bag_path: str, progress_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
    """
    Attempt to repair a corrupted bag file using ros2 bag tools.

    Args:
        bag_path: Path to the bag file or directory
        progress_callback: Optional callback function for progress updates

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        path_obj = Path(bag_path)

        if not path_obj.exists():
            return False, "ファイルが存在しません"

        if progress_callback:
            progress_callback("修復を開始しています...")

        # For MCAP files, try to reindex
        if bag_path.endswith('.mcap') or (path_obj.is_dir() and list(path_obj.glob('*.mcap'))):
            # ROS2 bag doesn't have a built-in repair command for MCAP
            # We can try to convert to a new bag which will skip corrupted messages
            backup_path = str(path_obj) + "_backup"

            if progress_callback:
                progress_callback("バックアップを作成しています...")

            # Create backup
            if path_obj.is_file():
                import shutil
                shutil.copy2(bag_path, backup_path)
            else:
                import shutil
                shutil.copytree(bag_path, backup_path)

            if progress_callback:
                progress_callback("修復を試行しています...")

            # Try to read and rewrite the bag
            # This will skip corrupted messages
            output_path = str(path_obj) + "_repaired"

            cmd = [
                'ros2', 'bag', 'convert',
                '-i', bag_path,
                '-o', output_path,
                '--output-options', 'storage_id=mcap'
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )

                if result.returncode == 0:
                    if progress_callback:
                        progress_callback("修復が完了しました")

                    return True, f"修復されたファイルを作成しました: {output_path}\nバックアップ: {backup_path}"
                else:
                    return False, f"修復に失敗しました: {result.stderr}"

            except subprocess.TimeoutExpired:
                return False, "修復がタイムアウトしました（ファイルが大きすぎる可能性があります）"

        # For DB3 bags
        elif path_obj.is_dir() and list(path_obj.glob('*.db3')):
            if progress_callback:
                progress_callback("DB3形式の修復を試行しています...")

            # Try to reindex using sqlite
            return False, "DB3形式の自動修復は未実装です。手動で sqlite3 を使って修復してください。"

        else:
            return False, "サポートされていない形式です"

    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"


def compress_bag(bag_path: str, compression: str = "zstd",
                 progress_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
    """
    Compress a bag file.

    Args:
        bag_path: Path to the bag file or directory
        compression: Compression format ('zstd' or 'lz4')
        progress_callback: Optional callback function for progress updates

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if progress_callback:
            progress_callback("圧縮を開始しています...")

        output_path = str(Path(bag_path).with_suffix('')) + f"_compressed_{compression}"

        cmd = [
            'ros2', 'bag', 'convert',
            '-i', bag_path,
            '-o', output_path,
            '--output-options', f'storage_id=mcap,compression_format={compression},compression_mode=file'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        if result.returncode == 0:
            if progress_callback:
                progress_callback("圧縮が完了しました")

            return True, f"圧縮されたファイルを作成しました: {output_path}"
        else:
            return False, f"圧縮に失敗しました: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "圧縮がタイムアウトしました"
    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"
