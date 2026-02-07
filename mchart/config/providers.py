"""Provider-specific configuration classes"""

from typing import NotRequired
from .base import BaseConfig


class BillboardConfig(BaseConfig):
    """
    Configuration for Billboard provider (Scrapy-based)

    Inherits all options from BaseConfig and adds Billboard-specific options.
    All fields are optional.

    Examples:
        >>> config = {"timeout": 60, "include_images": False}
        >>> config = BillboardConfig(include_images=False, max_chart_entries=10)
    """

    include_images: NotRequired[bool]
    """Whether to fetch song/album cover image URLs, default: True"""

    max_chart_entries: NotRequired[int | None]
    """Limit the number of chart entries returned, None means return all, default: None"""

    fallback_to_default: NotRequired[bool]
    """Whether to fall back to Hot 100 when requested chart doesn't exist, default: True"""


# Default configuration values
DEFAULT_BILLBOARD_CONFIG: BillboardConfig = {
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "verify_ssl": True,
    "proxy": None,
    "enable_cache": False,
    "cache_ttl": 3600,
    "include_images": True,
    "max_chart_entries": None,
    "fallback_to_default": True,
}


class SpotifyConfig(BaseConfig):
    """
    Configuration for Spotify provider
    
    Inherits all options from BaseConfig and adds Spotify-specific options.
    All fields are optional.
    
    Examples:
        >>> config = {"client_id": "your_id", "client_secret": "your_secret"}
        >>> config = SpotifyConfig(market="CN", auto_refresh_token=False)
    """
    
    client_id: NotRequired[str | None]
    """Spotify API Client ID"""
    
    client_secret: NotRequired[str | None]
    """Spotify API Client Secret"""
    
    market: NotRequired[str]
    """Market/region code, e.g., 'US', 'GB', 'CN', default: US"""
    
    access_token: NotRequired[str | None]
    """If you already have an access token, provide it directly to avoid re-authentication"""
    
    auto_refresh_token: NotRequired[bool]
    """Whether to automatically refresh token when expired, default: True"""


# Default configuration values
DEFAULT_SPOTIFY_CONFIG: SpotifyConfig = {
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "verify_ssl": True,
    "proxy": None,
    "enable_cache": False,
    "cache_ttl": 3600,
    "client_id": None,
    "client_secret": None,
    "market": "US",
    "access_token": None,
    "auto_refresh_token": True,
}
