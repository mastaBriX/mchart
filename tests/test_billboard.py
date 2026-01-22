"""Tests for Billboard provider"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
from bs4 import BeautifulSoup

from mchart.providers.billboard import BillboardProvider
from mchart.models import Chart, ChartMetadata, ChartEntry


class TestBillboardProvider:
    """Tests for BillboardProvider"""
    
    def test_provider_initialization(self):
        """Test creating BillboardProvider"""
        provider = BillboardProvider()
        assert provider.name == "billboard"
        assert provider is not None
    
    def test_provider_with_config(self):
        """Test creating provider with config"""
        config = {"timeout": 60, "parser": "html.parser"}
        provider = BillboardProvider(config)
        assert provider.config["timeout"] == 60
    
    def test_get_chart_type_single(self):
        """Test identifying single chart type"""
        provider = BillboardProvider()
        assert provider._get_chart_type("hot-100") == "single"
        assert provider._get_chart_type("global-200") == "single"
    
    def test_get_chart_type_album(self):
        """Test identifying album chart type"""
        provider = BillboardProvider()
        assert provider._get_chart_type("billboard-200") == "album"
    
    def test_normalize_chart_name(self):
        """Test chart name normalization"""
        provider = BillboardProvider()
        assert provider._normalize_chart_name("hot-100") == "hot-100"
        assert provider._normalize_chart_name("Hot 100") == "hot-100"
        assert provider._normalize_chart_name("HOT_100") == "hot-100"
    
    def test_list_available_charts(self):
        """Test listing available charts"""
        provider = BillboardProvider()
        charts = provider.list_available_charts()
        assert isinstance(charts, list)
        assert len(charts) > 0
        
        # Check that each chart has type field
        for chart in charts:
            assert isinstance(chart, ChartMetadata)
            assert chart.type in ["single", "album"]
            assert chart.provider == "billboard"
        
        # Check specific charts
        chart_names = [c.title.lower() for c in charts]
        assert any("hot 100" in name for name in chart_names)
        assert any("200" in name for name in chart_names)
    
    def test_list_available_charts_type_field(self):
        """Test that list_available_charts sets correct type field"""
        provider = BillboardProvider()
        charts = provider.list_available_charts()
        
        # Find billboard-200 chart
        bb200 = next((c for c in charts if "200" in c.title), None)
        if bb200:
            assert bb200.type == "album"
        
        # Find hot-100 chart
        hot100 = next((c for c in charts if "hot 100" in c.title.lower()), None)
        if hot100:
            assert hot100.type == "single"
    
    @patch('mchart.providers.billboard.BillboardProvider._parse_entries')
    @patch('mchart.providers.billboard.BillboardProvider._parse_date')
    @patch('mchart.providers.billboard.BeautifulSoup')
    @patch('requests.Session')
    def test_get_latest_single_chart(self, mock_session_class, mock_soup, mock_parse_date, mock_parse_entries):
        """Test getting latest single chart"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Mock BeautifulSoup instance - find() should return None for meta tag
        mock_soup_instance = Mock()
        mock_soup_instance.find.return_value = None  # No meta description found
        mock_soup.return_value = mock_soup_instance
        
        mock_parse_date.return_value = date(2026, 1, 21)
        mock_parse_entries.return_value = []
        
        provider = BillboardProvider()
        chart = provider.get_latest("hot-100")
        
        assert isinstance(chart, Chart)
        assert chart.metadata.type == "single"
        assert chart.metadata.title == "Billboard Hot 100"
        mock_parse_entries.assert_called_once()
    
    @patch('mchart.providers.billboard.BillboardProvider._parse_album_entries')
    @patch('mchart.providers.billboard.BillboardProvider._parse_date')
    @patch('mchart.providers.billboard.BeautifulSoup')
    @patch('requests.Session')
    def test_get_latest_album_chart(self, mock_session_class, mock_soup, mock_parse_date, mock_parse_album_entries):
        """Test getting latest album chart"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Mock BeautifulSoup instance - find() should return None for meta tag
        mock_soup_instance = Mock()
        mock_soup_instance.find.return_value = None  # No meta description found
        mock_soup.return_value = mock_soup_instance
        
        mock_parse_date.return_value = date(2026, 1, 21)
        mock_parse_album_entries.return_value = []
        
        provider = BillboardProvider()
        chart = provider.get_latest("billboard-200")
        
        assert isinstance(chart, Chart)
        assert chart.metadata.type == "album"
        assert chart.metadata.title == "Billboard 200"
        mock_parse_album_entries.assert_called_once()
    
    @patch('mchart.providers.billboard.BillboardProvider._parse_entries')
    @patch('mchart.providers.billboard.BillboardProvider._parse_date')
    @patch('mchart.providers.billboard.BeautifulSoup')
    @patch('requests.Session')
    def test_get_chart_invalid_name(self, mock_session_class, mock_soup, mock_parse_date, mock_parse_entries):
        """Test getting chart with invalid name (should fallback to hot-100)"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Mock BeautifulSoup instance - find() should return None for meta tag
        mock_soup_instance = Mock()
        mock_soup_instance.find.return_value = None  # No meta description found
        mock_soup.return_value = mock_soup_instance
        
        mock_parse_date.return_value = date(2026, 1, 21)
        mock_parse_entries.return_value = []
        
        provider = BillboardProvider()
        # With fallback enabled (default), invalid chart name falls back to hot-100
        chart = provider.get_latest("invalid-chart-that-does-not-exist")
        # Should fallback to hot-100, which is a single chart
        assert chart.metadata.type == "single"
        assert chart.metadata.title == "Billboard Hot 100"
    
    def test_get_chart_invalid_name_no_fallback(self):
        """Test getting chart with invalid name when fallback is disabled"""
        config = {"fallback_to_default": False}
        provider = BillboardProvider(config)
        # When fallback is disabled, should raise ValueError
        with pytest.raises(ValueError):
            provider.get_latest("invalid-chart-that-does-not-exist")
    
    def test_close(self):
        """Test closing provider"""
        provider = BillboardProvider()
        provider.close()  # Should not raise error
