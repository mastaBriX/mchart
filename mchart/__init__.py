"""
MChart - A unified music chart data library

Supports fetching music chart data from multiple sources including Billboard, Spotify, and more.
"""

from .client import MChart
from .models import Chart, ChartEntry, Song, ChartMetadata
from .config import BaseConfig, BillboardConfig, SpotifyConfig

__version__ = "0.3.0"
__all__ = [
    "MChart",
    "Chart",
    "ChartEntry",
    "Song",
    "ChartMetadata",
    "BaseConfig",
    "BillboardConfig",
    "SpotifyConfig",
]
