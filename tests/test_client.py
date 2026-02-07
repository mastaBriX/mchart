"""Tests for MChart client"""

import pytest
from unittest.mock import patch
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

    def test_list_charts(self):
        """Test listing charts"""
        client = MChart()
        charts = client.list_charts("billboard")
        assert isinstance(charts, list)
        assert len(charts) > 0
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

    @patch("mchart.providers.billboard.run_spider")
    def test_get_chart_dict(self, mock_run_spider):
        """Test getting chart as dict"""
        mock_run_spider.return_value = [{
            "provider": "billboard",
            "chart_name": "hot-100",
            "chart_title": "Billboard Hot 100",
            "chart_type": "single",
            "description": "The week's most popular songs",
            "url": "https://www.billboard.com/charts/hot-100",
            "published_date": date(2026, 1, 21),
            "entries": [{
                "rank": 1,
                "title": "Test Song",
                "artist": "Test Artist",
                "artists": ["Test Artist"],
                "image": "",
                "weeks_on_chart": 1,
                "last_week": 0,
                "peak_position": 1,
                "entry_type": "song",
            }],
        }]

        client = MChart()
        chart = client.get_chart("billboard", "hot-100")

        assert isinstance(chart, dict)
        assert chart["metadata"]["title"] == "Billboard Hot 100"
        assert chart["metadata"]["type"] == "single"
        assert len(chart["entries"]) == 1

    @patch("mchart.providers.billboard.run_spider")
    def test_get_chart_model(self, mock_run_spider):
        """Test getting chart as model"""
        mock_run_spider.return_value = [{
            "provider": "billboard",
            "chart_name": "hot-100",
            "chart_title": "Billboard Hot 100",
            "chart_type": "single",
            "description": "The week's most popular songs",
            "url": "https://www.billboard.com/charts/hot-100",
            "published_date": date(2026, 1, 21),
            "entries": [{
                "rank": 1,
                "title": "Test Song",
                "artist": "Test Artist",
                "artists": ["Test Artist"],
                "image": "",
                "weeks_on_chart": 1,
                "last_week": 0,
                "peak_position": 1,
                "entry_type": "song",
            }],
        }]

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
        client.close()
