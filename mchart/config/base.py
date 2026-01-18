"""Base configuration class with common options for all providers"""

from typing import TypedDict, NotRequired


class BaseConfig(TypedDict, total=False):
    """
    Base configuration class for all providers
    
    Contains common HTTP request options like timeout, retries, User-Agent, etc.
    All fields are optional, users can pass only the options they want to customize.
    
    Examples:
        >>> config = {"timeout": 60, "max_retries": 5}
        >>> config = BaseConfig(timeout=60, max_retries=5)
    """
    
    timeout: NotRequired[int]
    """HTTP request timeout in seconds, default: 30"""
    
    max_retries: NotRequired[int]
    """Maximum number of retries on request failure, default: 3"""
    
    user_agent: NotRequired[str]
    """User-Agent header for HTTP requests"""
    
    verify_ssl: NotRequired[bool]
    """Whether to verify SSL certificates, default: True"""
    
    proxy: NotRequired[str | None]
    """HTTP proxy address, format: 'http://proxy.example.com:8080'"""
    
    enable_cache: NotRequired[bool]
    """Whether to enable response caching, default: False"""
    
    cache_ttl: NotRequired[int]
    """Cache TTL in seconds, default: 3600"""


# Default configuration values
DEFAULT_BASE_CONFIG: BaseConfig = {
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "verify_ssl": True,
    "proxy": None,
    "enable_cache": False,
    "cache_ttl": 3600,
}
