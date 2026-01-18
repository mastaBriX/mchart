"""Main MChart client

Provides a unified interface to access multiple chart data providers
"""

from typing import Any, Optional, Literal
from datetime import date

from .providers import BillboardProvider, SpotifyProvider, BaseProvider
from .config import BillboardConfig, SpotifyConfig
from .models import Chart, ChartMetadata


class MChart:
    """
    Main client for accessing music chart data
    
    Supports multiple providers (Billboard, Spotify, etc.) with a unified interface.
    Returns data as dicts by default for easy JSON serialization, but can also
    return Pydantic models for type-safe operations.
    
    Examples:
        >>> # Basic usage with default config
        >>> client = MChart()
        >>> chart = client.get_chart("billboard", "hot-100")
        >>> print(chart["metadata"]["title"])
        
        >>> # With custom config
        >>> config = {"billboard": {"timeout": 60, "parser": "html.parser"}}
        >>> client = MChart(config)
        
        >>> # Get as Pydantic model
        >>> chart = client.get_chart("billboard", "hot-100", return_type="model")
        >>> print(chart.total_entries)
    """
    
    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize MChart client
        
        Args:
            config: Provider configurations, format:
                {
                    "billboard": BillboardConfig,
                    "spotify": SpotifyConfig,
                }
        """
        self._config = config or {}
        self._providers: dict[str, BaseProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize all available providers"""
        # Initialize Billboard (always available)
        billboard_config = self._config.get("billboard")
        try:
            self._providers["billboard"] = BillboardProvider(billboard_config)
        except Exception as e:
            print(f"Warning: Failed to initialize Billboard provider: {e}")
        
        # Initialize Spotify (if configured)
        spotify_config = self._config.get("spotify")
        if spotify_config and spotify_config.get("client_id"):
            try:
                self._providers["spotify"] = SpotifyProvider(spotify_config)
            except Exception as e:
                print(f"Warning: Failed to initialize Spotify provider: {e}")
    
    @property
    def providers(self) -> list[str]:
        """
        Get list of available provider names
        
        Returns:
            List of provider names, e.g., ['billboard', 'spotify']
        """
        return list(self._providers.keys())
    
    def get_provider(self, provider: str) -> BaseProvider:
        """
        Get a provider instance
        
        Args:
            provider: Provider name
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider is not available
        """
        if provider not in self._providers:
            raise ValueError(
                f"Provider '{provider}' is not available. "
                f"Available providers: {self.providers}"
            )
        return self._providers[provider]
    
    def get_chart(
        self,
        provider: str,
        chart_name: str,
        return_type: Literal["dict", "model"] = "dict",
        **kwargs
    ) -> dict[str, Any] | Chart:
        """
        Get the latest chart data from a provider
        
        Args:
            provider: Provider name (e.g., 'billboard', 'spotify')
            chart_name: Chart name (e.g., 'hot-100', 'billboard-200')
            return_type: Return format - 'dict' for JSON-serializable dict (default),
                        'model' for Pydantic Chart model
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chart data as dict or Chart model depending on return_type
            
        Raises:
            ValueError: If provider is not available
            Exception: If fetching chart data fails
            
        Examples:
            >>> # Get as dict (default)
            >>> chart = client.get_chart("billboard", "hot-100")
            >>> print(chart["entries"][0]["song"]["title"])
            
            >>> # Get as Pydantic model
            >>> chart = client.get_chart("billboard", "hot-100", return_type="model")
            >>> print(chart.entries[0].song.title)
        """
        provider_instance = self.get_provider(provider)
        chart = provider_instance.get_latest(chart_name, **kwargs)
        
        if return_type == "dict":
            return chart.to_dict()
        else:
            return chart
    
    def get_chart_by_date(
        self,
        provider: str,
        chart_name: str,
        chart_date: date,
        return_type: Literal["dict", "model"] = "dict",
        **kwargs
    ) -> dict[str, Any] | Chart:
        """
        Get chart data for a specific date
        
        Args:
            provider: Provider name
            chart_name: Chart name
            chart_date: Chart date
            return_type: Return format - 'dict' or 'model'
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chart data as dict or Chart model
            
        Raises:
            NotImplementedError: If provider doesn't support historical data
            ValueError: If provider is not available
            Exception: If fetching chart data fails
        """
        provider_instance = self.get_provider(provider)
        chart = provider_instance.get_chart(chart_name, chart_date, **kwargs)
        
        if return_type == "dict":
            return chart.to_dict()
        else:
            return chart
    
    def list_charts(
        self,
        provider: str,
        return_type: Literal["dict", "model"] = "dict"
    ) -> list[dict[str, Any]] | list[ChartMetadata]:
        """
        List all available charts from a provider
        
        Args:
            provider: Provider name
            return_type: Return format - 'dict' or 'model'
            
        Returns:
            List of chart metadata as dicts or ChartMetadata models
            
        Raises:
            ValueError: If provider is not available
            NotImplementedError: If provider doesn't support listing charts
            
        Examples:
            >>> charts = client.list_charts("billboard")
            >>> for chart in charts:
            ...     print(f"{chart['title']}: {chart['description']}")
        """
        provider_instance = self.get_provider(provider)
        charts = provider_instance.list_available_charts()
        
        if return_type == "dict":
            return [chart.to_dict() for chart in charts]
        else:
            return charts
    
    def list_all_charts(
        self,
        return_type: Literal["dict", "model"] = "dict"
    ) -> dict[str, list[dict[str, Any]] | list[ChartMetadata]]:
        """
        List all available charts from all providers
        
        Args:
            return_type: Return format - 'dict' or 'model'
            
        Returns:
            Dict mapping provider names to their available charts
            
        Examples:
            >>> all_charts = client.list_all_charts()
            >>> for provider, charts in all_charts.items():
            ...     print(f"{provider}: {len(charts)} charts")
        """
        result = {}
        for provider_name in self.providers:
            try:
                result[provider_name] = self.list_charts(provider_name, return_type)
            except Exception as e:
                print(f"Warning: Failed to list charts for {provider_name}: {e}")
        return result
    
    def close(self) -> None:
        """
        Close all provider connections and release resources
        
        Should be called when done using the client, or use as context manager
        """
        for provider in self._providers.values():
            try:
                provider.close()
            except Exception:
                pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
    
    def __repr__(self) -> str:
        """String representation"""
        return f"MChart(providers={self.providers})"
