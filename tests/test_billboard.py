"""Tests for Billboard provider (Scrapy-based)"""

import pytest
from unittest.mock import patch
from datetime import date

from mchart.providers.billboard import BillboardProvider
from mchart.models import Chart, ChartMetadata, ChartEntry
from mchart.spiders.billboard import BillboardSpider


class TestBillboardProvider:
    """Tests for BillboardProvider"""

    def test_provider_initialization(self):
        """Test creating BillboardProvider"""
        provider = BillboardProvider()
        assert provider.name == "billboard"
        assert provider is not None

    def test_provider_with_config(self):
        """Test creating provider with config"""
        config = {"timeout": 60, "include_images": False}
        provider = BillboardProvider(config)
        assert provider.config["timeout"] == 60
        assert provider.config["include_images"] is False

    def test_scrapy_settings_from_config(self):
        """Test that provider config maps to Scrapy settings"""
        config = {"timeout": 45, "max_retries": 5, "user_agent": "TestAgent/1.0"}
        provider = BillboardProvider(config)
        assert provider._scrapy_settings["DOWNLOAD_TIMEOUT"] == 45
        assert provider._scrapy_settings["RETRY_TIMES"] == 5
        assert provider._scrapy_settings["USER_AGENT"] == "TestAgent/1.0"

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

        for chart in charts:
            assert isinstance(chart, ChartMetadata)
            assert chart.type in ["single", "album"]
            assert chart.provider == "billboard"

        chart_names = [c.title.lower() for c in charts]
        assert any("hot 100" in name for name in chart_names)
        assert any("200" in name for name in chart_names)

    def test_list_available_charts_type_field(self):
        """Test that list_available_charts sets correct type field"""
        provider = BillboardProvider()
        charts = provider.list_available_charts()

        bb200 = next((c for c in charts if "200" in c.title), None)
        if bb200:
            assert bb200.type == "album"

        hot100 = next((c for c in charts if "hot 100" in c.title.lower()), None)
        if hot100:
            assert hot100.type == "single"

    @patch("mchart.providers.billboard.run_spider")
    def test_get_latest_single_chart(self, mock_run_spider, raw_single_spider_result):
        """Test getting latest single chart"""
        mock_run_spider.return_value = [raw_single_spider_result]

        provider = BillboardProvider()
        chart = provider.get_latest("hot-100")

        assert isinstance(chart, Chart)
        assert chart.metadata.type == "single"
        assert chart.metadata.title == "Billboard Hot 100"
        mock_run_spider.assert_called_once()

    @patch("mchart.providers.billboard.run_spider")
    def test_get_latest_album_chart(self, mock_run_spider, raw_album_spider_result):
        """Test getting latest album chart"""
        mock_run_spider.return_value = [raw_album_spider_result]

        provider = BillboardProvider()
        chart = provider.get_latest("billboard-200")

        assert isinstance(chart, Chart)
        assert chart.metadata.type == "album"
        assert chart.metadata.title == "Billboard 200"
        assert len(chart.entries) == 1
        assert chart.entries[0].album is not None
        assert chart.entries[0].album.title == "Test Album"

    @patch("mchart.providers.billboard.run_spider")
    def test_get_latest_passes_spider_kwargs(self, mock_run_spider, raw_single_spider_result):
        """Test that get_latest passes correct kwargs to spider runner"""
        mock_run_spider.return_value = [raw_single_spider_result]

        config = {"include_images": False, "max_chart_entries": 10}
        provider = BillboardProvider(config)
        provider.get_latest("hot-100")

        call_kwargs = mock_run_spider.call_args
        assert call_kwargs.kwargs["chart_name"] == "hot-100"
        assert call_kwargs.kwargs["include_images"] is False
        assert call_kwargs.kwargs["max_chart_entries"] == 10

    @patch("mchart.providers.billboard.run_spider")
    def test_get_latest_invalid_name_fallback(self, mock_run_spider, raw_single_spider_result):
        """Test getting chart with invalid name (should fallback to hot-100)"""
        mock_run_spider.return_value = [raw_single_spider_result]

        provider = BillboardProvider()
        chart = provider.get_latest("invalid-chart-that-does-not-exist")

        assert chart.metadata.type == "single"
        call_kwargs = mock_run_spider.call_args
        assert call_kwargs.kwargs["chart_name"] == "hot-100"

    def test_get_chart_invalid_name_no_fallback(self):
        """Test getting chart with invalid name when fallback is disabled"""
        config = {"fallback_to_default": False}
        provider = BillboardProvider(config)
        with pytest.raises(ValueError):
            provider.get_latest("invalid-chart-that-does-not-exist")

    @patch("mchart.providers.billboard.run_spider")
    def test_get_latest_no_results_raises(self, mock_run_spider):
        """Test that empty spider results raise an exception"""
        mock_run_spider.return_value = []

        provider = BillboardProvider()
        with pytest.raises(Exception, match="no data returned"):
            provider.get_latest("hot-100")

    def test_get_chart_historical_not_supported(self):
        """Test that historical charts raise NotImplementedError"""
        provider = BillboardProvider()
        with pytest.raises(NotImplementedError):
            provider.get_chart("hot-100", date(2026, 1, 1))

    def test_close(self):
        """Test closing provider"""
        provider = BillboardProvider()
        provider.close()

    def test_assemble_chart_single(self, raw_single_spider_result):
        """Test assembling a Chart from raw single chart data"""
        provider = BillboardProvider()
        chart = provider._assemble_chart(raw_single_spider_result)

        assert isinstance(chart, Chart)
        assert chart.metadata.provider == "billboard"
        assert chart.chart_type == "single"
        assert len(chart.entries) == 1
        assert chart.entries[0].song is not None
        assert chart.entries[0].song.title == "Test Song"
        assert chart.entries[0].song.artist == "Test Artist"
        assert chart.entries[0].rank == 1

    def test_assemble_chart_album(self, raw_album_spider_result):
        """Test assembling a Chart from raw album chart data"""
        provider = BillboardProvider()
        chart = provider._assemble_chart(raw_album_spider_result)

        assert isinstance(chart, Chart)
        assert chart.chart_type == "album"
        assert len(chart.entries) == 1
        assert chart.entries[0].album is not None
        assert chart.entries[0].album.title == "Test Album"


class TestBillboardSpider:
    """Tests for BillboardSpider"""

    def test_spider_defaults(self):
        """Test spider default configuration"""
        spider = BillboardSpider()
        assert spider.chart_name == "hot-100"
        assert spider.include_images is True
        assert spider.max_chart_entries is None

    def test_spider_with_params(self):
        """Test spider with custom parameters"""
        spider = BillboardSpider(
            chart_name="billboard-200",
            include_images=False,
            max_chart_entries=10,
        )
        assert spider.chart_name == "billboard-200"
        assert spider.include_images is False
        assert spider.max_chart_entries == 10

    def test_spider_chart_urls(self):
        """Test that spider has all expected chart URLs"""
        assert "hot-100" in BillboardSpider.CHART_URLS
        assert "billboard-200" in BillboardSpider.CHART_URLS
        assert "global-200" in BillboardSpider.CHART_URLS

    def test_spider_album_charts(self):
        """Test that billboard-200 is recognized as album chart"""
        assert "billboard-200" in BillboardSpider.ALBUM_CHARTS

    def test_split_artists_ampersand(self):
        """Test splitting artists by ampersand"""
        spider = BillboardSpider()
        assert spider._split_artists("Artist A & Artist B") == [
            "Artist A", "Artist B"
        ]

    def test_split_artists_comma(self):
        """Test splitting artists by comma"""
        spider = BillboardSpider()
        assert spider._split_artists("Artist A, Artist B") == [
            "Artist A", "Artist B"
        ]

    def test_split_artists_single(self):
        """Test single artist passthrough"""
        spider = BillboardSpider()
        assert spider._split_artists("Solo Artist") == ["Solo Artist"]
