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

        # MCAPファイルの場合、再インデックスを試みる
        if bag_path.endswith('.mcap') or (path_obj.is_dir() and list(path_obj.glob('*.mcap'))):
            # ROS2 bagにはMCAP用の組み込み修復コマンドがない
            # 破損したメッセージをスキップして新しいbagに変換する

            # 重複しないバックアップパスを作成
            backup_base = str(path_obj) + "_backup"
            backup_path = backup_base
            counter = 1
            while Path(backup_path).exists():
                backup_path = f"{backup_base}_{counter}"
                counter += 1

            if progress_callback:
                progress_callback("バックアップを作成しています...")

            # バックアップを作成
            if path_obj.is_file():
                import shutil
                shutil.copy2(bag_path, backup_path)
            else:
                import shutil
                shutil.copytree(bag_path, backup_path)

            if progress_callback:
                progress_callback("修復を試行しています...")

            # bagを読み込んで再書き込み
            # これにより破損したメッセージがスキップされる
            import tempfile
            import yaml

            # 重複しない出力パスを作成
            output_base = str(path_obj) + "_repaired"
            output_path = output_base
            counter = 1
            while Path(output_path).exists():
                output_path = f"{output_base}_{counter}"
                counter += 1

            # YAML設定を作成
            config = {
                'output_bags': [
                    {
                        'uri': output_path,
                        'storage_id': 'mcap',
                        'compression_format': '',  # No compression for repaired bags
                        'compression_mode': 'none'
                    }
                ]
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f)
                config_file = f.name

            try:
                # 入力ストレージは常にMCAP（DB3は非サポート）
                input_storage = 'mcap'

                cmd = [
                    'ros2', 'bag', 'convert',
                    '-i', bag_path, input_storage,
                    '-o', config_file
                ]

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
                    error_msg = result.stderr if result.stderr else result.stdout
                    return False, f"修復に失敗しました:\n{error_msg}"

            except subprocess.TimeoutExpired:
                return False, "修復がタイムアウトしました（ファイルが大きすぎる可能性があります）"
            finally:
                try:
                    Path(config_file).unlink()
                except:
                    pass

        # DB3 bag（現在は非サポート）
        elif path_obj.is_dir() and list(path_obj.glob('*.db3')):
            if progress_callback:
                progress_callback("DB3形式の修復を試行しています...")

            # sqliteを使用した再インデックス
            return False, "DB3形式の自動修復は未実装です。手動で sqlite3 を使って修復してください。"

        else:
            return False, "サポートされていない形式です"

    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"


def compress_bag(bag_path: str, compression: str = "zstd",
                 progress_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
    """
    Compress a bag file using mcap compress command.
    Deletes the original directory/file and renames the compressed file to the original name.

    Args:
        bag_path: Path to the bag file or directory
        compression: Compression format ('zstd' or 'lz4')
        progress_callback: Optional callback function for progress updates

    Returns:
        Tuple of (success: bool, message: str)
    """
    import shutil

    try:
        if progress_callback:
            progress_callback("圧縮を開始しています...")

        bag_path_obj = Path(bag_path)
        is_directory = bag_path_obj.is_dir()

        # Find the actual .mcap file
        mcap_file = None
        if is_directory:
            # Find .mcap files in directory (ROS2 bag format)
            mcap_files = [f for f in bag_path_obj.iterdir()
                          if f.is_file() and f.suffix == '.mcap']
            if mcap_files:
                mcap_files.sort()
                mcap_file = mcap_files[0]
        elif bag_path_obj.is_file() and '.mcap' in bag_path_obj.name:
            mcap_file = bag_path_obj

        if not mcap_file:
            return False, "MCAPファイルが見つかりません"

        # Create temporary output filename in parent directory to avoid deletion
        # when removing the source directory
        temp_output_file = bag_path_obj.parent / f"_compress_tmp_{bag_path_obj.name}.{compression}"

        if progress_callback:
            progress_callback(f"圧縮中: {mcap_file.name}")

        # Use mcap compress command
        cmd = [
            'mcap', 'compress',
            str(mcap_file),
            '-o', str(temp_output_file),
            '--compression', compression
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            # Clean up temporary file if it exists
            if temp_output_file.exists():
                temp_output_file.unlink()
            return False, f"mcap compressコマンドが失敗しました:\nコマンド: {' '.join(cmd)}\nエラー: {error_msg}"

        # Check if output file was created
        if not temp_output_file.exists():
            return False, f"圧縮ファイルが作成されませんでした:\n期待されるパス: {temp_output_file}"

        if progress_callback:
            progress_callback("圧縮が完了しました。元のファイルを削除して名前を変更しています...")

        # Get file sizes for comparison before deletion
        original_size = mcap_file.stat().st_size
        compressed_size = temp_output_file.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        # Determine final output path
        if is_directory:
            # If original was a directory, create new name based on directory
            final_output = bag_path_obj.parent / f"{bag_path_obj.name}.mcap.{compression}"
        else:
            # If original was a file, replace it with compressed version
            # Remove .mcap extension and add .mcap.zstd
            final_output = mcap_file.parent / f"{mcap_file.stem}.mcap.{compression}"

        # Delete original (directory or file)
        if is_directory:
            shutil.rmtree(bag_path_obj)
        else:
            mcap_file.unlink()

        # Move compressed file to final name (use shutil.move for cross-directory moves)
        shutil.move(str(temp_output_file), str(final_output))

        if progress_callback:
            progress_callback("完了")

        from susumu_bag_cabinet.utils.bag_utils import format_size
        return True, f"圧縮完了:\n元のサイズ: {format_size(original_size)}\n圧縮後: {format_size(compressed_size)}\n圧縮率: {ratio:.1f}%\n\n新しいファイル名: {final_output.name}"

    except subprocess.TimeoutExpired:
        return False, "圧縮がタイムアウトしました"
    except Exception as e:
        import traceback
        return False, f"エラーが発生しました: {str(e)}\n{traceback.format_exc()}"
