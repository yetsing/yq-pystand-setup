#!/usr/bin/env python3
import pathlib
import sys

from setuptools import setup

# 需要给所有文件读写操作都指定编码，避免 windows gbk 编码错误
utf8 = "utf-8"
script_directory = pathlib.Path(__file__).resolve().parent
is_windows = sys.platform.startswith("win32")
long_description = script_directory.joinpath("README.md").read_text(encoding=utf8)


def get_version() -> str:
    version_filepath = script_directory.joinpath("yq_pystand_setup", "_version.py")
    version_dict = {}
    exec(version_filepath.read_text(encoding=utf8), {}, version_dict)
    return version_dict["__version__"]


setup(
    name="yq_pystand_setup",
    description="Setup PyStand",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=get_version(),
    url="https://github.com/yetsing/yq-pystand-setup",
    author="yeqing",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.7",
    keywords=["pystand"],
    packages=[
        "yq_pystand_setup",
    ],
)