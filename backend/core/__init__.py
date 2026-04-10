"""Core __init__ file"""

from .config import settings
from .logger import setup_logging

__all__ = ["settings", "setup_logging"]
