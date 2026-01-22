"""Tests for MChart client"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from mchart import MChart
from mchart.models import Chart, ChartMetadata, ChartEntry, Song, Album


class TestMChart:
    """Tests for MChart client"""
    
    def test_client_initialization(self):
        """Test creating MChart client"""
        client = MChart()
        assert client is not None
        assert "billboard" in client.providers
    
    def test_client_with_config(self):
        """Test creating client with config"""
        config = {"billboard": {"timeout": 60}}
        client = MChart(config)
        assert client is not None
    
    def test_client_context_manager(self):
        """Test using client as context manager"""
        with MChart() as client:
            assert client is not None
        # Should close without error
    
    def test_list_charts(self):
        """Test listing charts"""
        client = MChart()
        charts = client.list_charts("billboard")
        assert isinstance(charts, list)
        assert len(charts) > 0
        # Check that each chart has required fields
        for chart in charts:
            assert "title" in chart
            assert "provider" in chart
            assert "type" in chart
    
    def test_list_all_charts(self):
        """Test listing all charts from all providers"""
        client = MChart()
        all_charts = client.list_all_charts()
        assert isinstance(all_charts, dict)
        assert "billboard" in all_charts
    
    @patch('mchart.providers.billboard.BillboardProvider.get_latest')
    def test_get_chart_dict(self, mock_get_latest):
        """Test getting chart as dict"""
        # Mock the provider response
        mock_chart = Chart(
            metadata=ChartMetadata(
                provider="billboard",
                title="Billboard Hot 100",
                type="single"
            ),
            published_date=date(2026, 1, 21),
            entries=[
                ChartEntry(
                    song=Song(title="Test Song", artist="Test Artist"),
                    rank=1,
                    weeks_on_chart=1
                )
            ]
        )
        mock_get_latest.return_value = mock_chart
        
        client = MChart()
        chart = client.get_chart("billboard", "hot-100")
        
        assert isinstance(chart, dict)
        assert chart["metadata"]["title"] == "Billboard Hot 100"
        assert chart["metadata"]["type"] == "single"
        assert len(chart["entries"]) == 1
    
    @patch('mchart.providers.billboard.BillboardProvider.get_latest')
    def test_get_chart_model(self, mock_get_latest):
        """Test getting chart as model"""
        # Mock the provider response
        mock_chart = Chart(
            metadata=ChartMetadata(
                provider="billboard",
                title="Billboard Hot 100",
                type="single"
            ),
            published_date=date(2026, 1, 21),
            entries=[
                ChartEntry(
                    song=Song(title="Test Song", artist="Test Artist"),
                    rank=1,
                    weeks_on_chart=1
                )
            ]
        )
        mock_get_latest.return_value = mock_chart
        
        client = MChart()
        chart = client.get_chart("billboard", "hot-100", return_type="model")
        
        assert isinstance(chart, Chart)
        assert chart.metadata.title == "Billboard Hot 100"
        assert chart.total_entries == 1
    
    def test_get_chart_invalid_provider(self):
        """Test getting chart with invalid provider"""
        client = MChart()
        with pytest.raises(ValueError):
            client.get_chart("invalid_provider", "hot-100")
    
    def test_close(self):
        """Test closing client"""
        client = MChart()
        client.close()  # Should not raise error
