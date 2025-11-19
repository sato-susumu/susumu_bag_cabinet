#!/usr/bin/env python3
"""
Test the browse functionality with actual bag files.
"""

import sys
from pathlib import Path
from susumu_bag_cabinet.utils.config import Config
from susumu_bag_cabinet.utils.bag_utils import scan_bag_folder, get_bag_info, format_size


def test_browse():
    """Test browsing bag files."""
    print("="*60)
    print("Testing Browse Functionality")
    print("="*60)

    config = Config()
    bag_folder = config.get_bag_folder()

    print(f"\nBag folder: {bag_folder}")

    # Scan for files
    print("\nScanning for bag files...")
    files = scan_bag_folder(bag_folder)
    print(f"Found {len(files)} bag files\n")

    if not files:
        print("No bag files found. Please add some bag files to test.")
        return

    # Get detailed info for each file
    print("Extracting detailed information:")
    print("-" * 60)

    for i, file_path in enumerate(files, 1):
        filename = Path(file_path).name
        print(f"\n[{i}] {filename}")

        info = get_bag_info(file_path)

        print(f"    Path: {file_path}")
        print(f"    Size: {format_size(info['size'])}")
        print(f"    Format: {info['format']}")
        print(f"    Start time: {info['start_time']}")
        print(f"    Compression: {info['compression']}")
        print(f"    Valid: {info['is_valid']}")

    print("\n" + "="*60)
    print("Browse test completed!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_browse()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
