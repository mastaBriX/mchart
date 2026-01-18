"""Base provider interface definition

All providers must implement this interface to ensure API consistency
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
from enum import Flag, auto

from ..models import Chart, ChartMetadata
from ..config import BaseConfig


class ProviderCapability(Flag):
    """Provider capability flags"""
    
    LATEST = auto()  # Supports fetching latest charts
    HISTORICAL = auto()  # Supports fetching historical charts
    LIST_CHARTS = auto()  # Supports listing available charts
    SEARCH = auto()  # Supports search functionality
    
    ALL = LATEST | HISTORICAL | LIST_CHARTS | SEARCH


class BaseProvider(ABC):
    """
    Base class for all chart data providers
    
    Defines standard interface methods that all providers must implement.
    Even if certain features are not supported, they should raise NotImplementedError with explanation.
    """
    
    def __init__(self, config: Optional[BaseConfig] = None):
        """
        Initialize provider
        
        Args:
            config: Provider configuration, uses default if None
        """
        self.config = config or BaseConfig()
        self._setup()
    
    @abstractmethod
    def _setup(self) -> None:
        """
        Setup initialization, such as creating HTTP session
        Subclasses must implement this method
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name, e.g., 'billboard', 'spotify'"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapability:
        """Return supported capabilities of the provider"""
        pass
    
    @abstractmethod
    def get_latest(self, chart_name: str, **kwargs) -> Chart:
        """
        Get the latest chart data
        
        Args:
            chart_name: Name of the chart
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chart object containing complete chart data
            
        Raises:
            ValueError: When chart name is invalid
            NotImplementedError: When provider doesn't support this feature
            Exception: Other errors
        """
        pass
    
    @abstractmethod
    def get_chart(
        self, 
        chart_name: str, 
        chart_date: date,
        **kwargs
    ) -> Chart:
        """
        Get chart data for a specific date
        
        Args:
            chart_name: Name of the chart
            chart_date: Chart date
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chart object containing complete chart data
            
        Raises:
            ValueError: When chart name or date is invalid
            NotImplementedError: When provider doesn't support historical data
            Exception: Other errors
        """
        pass
    
    @abstractmethod
    def list_available_charts(self) -> list[ChartMetadata]:
        """
        List all available charts
        
        Returns:
            List of ChartMetadata containing basic info about available charts
            
        Raises:
            NotImplementedError: When provider doesn't support this feature
            Exception: Other errors
        """
        pass
    
    def supports(self, capability: ProviderCapability) -> bool:
        """
        Check if provider supports a specific capability
        
        Args:
            capability: Capability to check
            
        Returns:
            True if supported, False otherwise
        """
        return bool(self.capabilities & capability)
    
    def close(self) -> None:
        """
        Close provider and release resources (e.g., close HTTP session)
        Optional implementation
        """
        pass
