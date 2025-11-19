"""
Utility functions for working with ROS2 bag files.
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


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
        "compression": "未チェック",
        "is_valid": "未チェック",
    }

    # Get file/directory size
    path_obj = Path(bag_path)
    if path_obj.exists():
        if path_obj.is_file():
            result["size"] = path_obj.stat().st_size
        elif path_obj.is_dir():
            result["size"] = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())

    # Detect format
    if bag_path.endswith('.mcap'):
        result["format"] = "MCAP"
    elif path_obj.is_dir() and (path_obj / 'metadata.yaml').exists():
        result["format"] = "ROS2"

    # Try to get metadata using ros2 bag info
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

            # Parse start time
            time_match = re.search(r'Start:\s+([^\n]+)', output)
            if time_match:
                time_str = time_match.group(1).strip()
                try:
                    # Try to parse the timestamp
                    # Format: "Jan 1 2025 12:34:56.789 (1234567890.123)"
                    # We'll extract the unix timestamp in parentheses if available
                    unix_match = re.search(r'\((\d+\.\d+)\)', time_str)
                    if unix_match:
                        timestamp = float(unix_match.group(1))
                        result["start_time"] = datetime.fromtimestamp(timestamp)
                    else:
                        # Try to parse the human-readable format
                        # This is a fallback and may not work for all formats
                        result["start_time"] = time_str
                except Exception:
                    result["start_time"] = time_str

            # Check for compression info
            if 'compression' in output.lower():
                if 'lz4' in output.lower():
                    result["compression"] = "圧縮(LZ4)"
                elif 'zstd' in output.lower():
                    result["compression"] = "圧縮(Zstd)"
                else:
                    result["compression"] = "未圧縮"
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

    return result


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def generate_filename(label: str = "", robot_name: str = "", include_robot: bool = False) -> str:
    """
    Generate a filename for a new bag recording.

    Args:
        label: Optional label to include in filename
        robot_name: Robot name (used if include_robot is True)
        include_robot: Whether to include robot name in filename

    Returns:
        Generated filename (without extension)
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
    Scan a folder for bag files.

    Args:
        folder_path: Path to the folder to scan

    Returns:
        List of bag file/directory paths
    """
    folder = Path(folder_path)
    if not folder.exists():
        return []

    bag_files = []

    # Find .mcap files
    bag_files.extend(str(p) for p in folder.glob('*.mcap'))

    # Find bag directories (containing metadata.yaml)
    for item in folder.iterdir():
        if item.is_dir() and (item / 'metadata.yaml').exists():
            bag_files.append(str(item))

    return sorted(bag_files, key=lambda x: Path(x).stat().st_mtime, reverse=True)
