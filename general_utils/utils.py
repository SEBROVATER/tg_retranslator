from functools import cache
from pathlib import Path


@cache
def get_base_dir() -> Path:
    base_dir = Path(__file__).parent.parent.absolute()
    return base_dir
