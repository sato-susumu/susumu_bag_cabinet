#!/usr/bin/env python3
"""
Basic test script to verify components work without GUI.
"""

import sys
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from susumu_bag_cabinet.utils.config import Config
    from susumu_bag_cabinet.utils.bag_utils import (
        scan_bag_folder, get_bag_info, generate_filename, format_size
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test config
print("\nTesting config...")
try:
    config = Config()
    print(f"✓ Config loaded")
    print(f"  Bag folder: {config.get_bag_folder()}")
    print(f"  Robot name: {config.get_robot_name()}")
    print(f"  Foxglove command: {config.get_foxglove_command()}")
except Exception as e:
    print(f"✗ Config test failed: {e}")
    sys.exit(1)

# Test bag scanning
print("\nTesting bag file scanning...")
try:
    bag_folder = config.get_bag_folder()
    if Path(bag_folder).exists():
        files = scan_bag_folder(bag_folder)
        print(f"✓ Found {len(files)} bag files:")
        for f in files[:5]:  # Show first 5
            print(f"  - {Path(f).name}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    else:
        print(f"! Bag folder does not exist: {bag_folder}")
        print("  Creating folder for testing...")
        Path(bag_folder).mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"✗ Bag scanning failed: {e}")
    sys.exit(1)

# Test filename generation
print("\nTesting filename generation...")
try:
    filename1 = generate_filename()
    print(f"✓ Default filename: {filename1}.mcap")

    filename2 = generate_filename(label="test_label")
    print(f"✓ With label: {filename2}.mcap")

    filename3 = generate_filename(label="test", robot_name="robot1", include_robot=True)
    print(f"✓ With robot name: {filename3}.mcap")
except Exception as e:
    print(f"✗ Filename generation failed: {e}")
    sys.exit(1)

# Test size formatting
print("\nTesting size formatting...")
try:
    print(f"✓ 1024 B = {format_size(1024)}")
    print(f"✓ 1048576 B = {format_size(1048576)}")
    print(f"✓ 1073741824 B = {format_size(1073741824)}")
except Exception as e:
    print(f"✗ Size formatting failed: {e}")
    sys.exit(1)

# Test bag info (if files exist)
print("\nTesting bag info extraction...")
if files:
    try:
        test_file = files[0]
        print(f"Getting info for: {Path(test_file).name}")
        info = get_bag_info(test_file)
        print(f"✓ Bag info retrieved:")
        print(f"  Format: {info.get('format')}")
        print(f"  Size: {format_size(info.get('size', 0))}")
        print(f"  Start time: {info.get('start_time')}")
        print(f"  Compression: {info.get('compression')}")
        print(f"  Valid: {info.get('is_valid')}")
    except Exception as e:
        print(f"✗ Bag info extraction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("! No bag files to test")

print("\n" + "="*50)
print("All basic tests completed successfully!")
print("="*50)
