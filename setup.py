#!/usr/bin/env python3
"""Setup script for Susumu Bag Cabinet."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="susumu-bag-cabinet",
    version="0.1.0",
    author="Susumu Bag Cabinet Team",
    description="ROS2 Bag File Management Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "susumu-bag-cabinet=susumu_bag_cabinet.main:main",
        ],
    },
)
