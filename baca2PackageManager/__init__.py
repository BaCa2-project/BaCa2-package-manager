from .manager import *
from pathlib import Path

import baca2PackageManager.consts as consts


def base_dir() -> Path:
    """
    Get base directory for package manager.

    :return: A path to directory.
    """
    if consts.BASE_DIR is None:
        raise ValueError("Base directory is not set")
    return consts.BASE_DIR


def set_base_dir(path: Path):
    """
    Set base directory for package manager.

    :param path: A path to directory.
    :return: None.
    """
    consts.BASE_DIR = path


def add_supported_extensions(*args):
    """
    Add supported extensions for package manager.

    :param args: A list of extensions.
    :return: None.
    """
    consts.SUPPORTED_EXTENSIONS.extend(args)
