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
            import tempfile
            import yaml

            output_path = str(path_obj) + "_repaired"

            # Create YAML config
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
                # Detect input storage
                input_storage = 'mcap'
                if Path(bag_path).is_dir() and list(Path(bag_path).glob('*.db3')):
                    input_storage = 'sqlite3'
                elif bag_path.endswith('.db3'):
                    input_storage = 'sqlite3'

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
    import tempfile
    import yaml

    try:
        if progress_callback:
            progress_callback("圧縮を開始しています...")

        # Get output path
        bag_name = Path(bag_path).stem if Path(bag_path).is_file() else Path(bag_path).name
        output_dir = Path(bag_path).parent
        output_path = output_dir / f"{bag_name}_compressed_{compression}"

        # Create YAML config file for ros2 bag convert
        config = {
            'output_bags': [
                {
                    'uri': str(output_path),
                    'storage_id': 'mcap',
                    'compression_format': compression,
                    'compression_mode': 'file'
                }
            ]
        }

        # Write config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_file = f.name

        try:
            # Detect input storage format
            input_storage = 'mcap'  # Default
            if Path(bag_path).is_dir():
                if list(Path(bag_path).glob('*.db3')):
                    input_storage = 'sqlite3'
                elif (Path(bag_path) / 'metadata.yaml').exists():
                    # Check what storage is used in the bag directory
                    mcap_files = list(Path(bag_path).glob('*.mcap'))
                    db3_files = list(Path(bag_path).glob('*.db3'))
                    if mcap_files:
                        input_storage = 'mcap'
                    elif db3_files:
                        input_storage = 'sqlite3'
            elif bag_path.endswith('.db3'):
                input_storage = 'sqlite3'

            cmd = [
                'ros2', 'bag', 'convert',
                '-i', bag_path, input_storage,
                '-o', config_file
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            if result.returncode == 0:
                if progress_callback:
                    progress_callback("圧縮が完了しました。ファイルを置き換えています...")

                # Rename original file to backup
                import shutil
                bag_path_obj = Path(bag_path)
                if bag_path_obj.is_file():
                    backup_path = bag_path_obj.parent / f"{bag_path_obj.stem}_uncompressed{bag_path_obj.suffix}"
                else:
                    backup_path = Path(str(bag_path) + "_uncompressed")

                # Move original to backup
                shutil.move(str(bag_path), str(backup_path))

                # Rename compressed file to original name
                shutil.move(str(output_path), str(bag_path))

                if progress_callback:
                    progress_callback("完了しました")

                return True, f"圧縮完了:\n元ファイル → {backup_path.name}\n圧縮版 → {bag_path_obj.name}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"圧縮に失敗しました:\n{error_msg}"

        finally:
            # Clean up temp file
            try:
                Path(config_file).unlink()
            except:
                pass

    except subprocess.TimeoutExpired:
        return False, "圧縮がタイムアウトしました"
    except Exception as e:
        import traceback
        return False, f"エラーが発生しました: {str(e)}\n{traceback.format_exc()}"
