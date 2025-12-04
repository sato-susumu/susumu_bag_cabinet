"""
Configuration management for Susumu Bag Cabinet.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Application configuration manager."""

    DEFAULT_CONFIG = {
        "bag_folder": str(Path.home() / "ros2_bags"),
        "robot_name": "",
        "foxglove_command": "foxglove-studio",
        "filename_include_robot_name": False,
        "glim_config_path": "/home/taro/ros2_ws/src/susumu_robo/mapping/config/livox",
        "glim_dump_path": "/glim",
    }

    def __init__(self):
        """Initialize configuration."""
        self.config_dir = Path.home() / ".config" / "susumu_bag_cabinet"
        self.config_file = self.config_dir / "config.json"
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()

        # Ensure all default keys exist
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value

    def save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def get_bag_folder(self) -> str:
        """Get the bag folder path."""
        return self.config.get("bag_folder", self.DEFAULT_CONFIG["bag_folder"])

    def set_bag_folder(self, path: str) -> None:
        """Set the bag folder path."""
        self.config["bag_folder"] = path

    def get_robot_name(self) -> str:
        """Get the robot name."""
        return self.config.get("robot_name", "")

    def set_robot_name(self, name: str) -> None:
        """Set the robot name."""
        self.config["robot_name"] = name

    def get_foxglove_command(self) -> str:
        """Get the Foxglove Studio command."""
        return self.config.get("foxglove_command", "foxglove-studio")

    def set_foxglove_command(self, command: str) -> None:
        """Set the Foxglove Studio command."""
        self.config["foxglove_command"] = command

    def get_folder_include_robot_name(self) -> bool:
        """Get whether to include robot name in filename."""
        return self.config.get("filename_include_robot_name", False)

    def set_filename_include_robot_name(self, include: bool) -> None:
        """Set whether to include robot name in filename."""
        self.config["filename_include_robot_name"] = include

    def get_glim_config_path(self) -> str:
        """Get the glim_rosbag config path."""
        return self.config.get("glim_config_path", self.DEFAULT_CONFIG["glim_config_path"])

    def set_glim_config_path(self, path: str) -> None:
        """Set the glim_rosbag config path."""
        self.config["glim_config_path"] = path

    def get_glim_dump_path(self) -> str:
        """Get the glim_rosbag dump_path base directory."""
        return self.config.get("glim_dump_path", self.DEFAULT_CONFIG["glim_dump_path"])

    def set_glim_dump_path(self, path: str) -> None:
        """Set the glim_rosbag dump_path base directory."""
        self.config["glim_dump_path"] = path
