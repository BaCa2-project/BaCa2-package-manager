from pathlib import Path

BASE_DIR: Path | None = None
SUPPORTED_EXTENSIONS = []

MEM_SIZES = {
    'B': 1,
    'K': 1024,
    'M': 1024 ** 2,
    'G': 1024 ** 3,
    'T': 1024 ** 4,
}