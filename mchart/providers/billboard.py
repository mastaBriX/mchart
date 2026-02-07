"""Billboard provider implementation

Uses Scrapy spider to scrape chart data from billboard.com.
"""

from datetime import date
from typing import Optional
import warnings

from .base import BaseProvider, ProviderCapability
from ..models import Chart, ChartEntry, ChartMetadata, Song, Album
from ..config import BillboardConfig, DEFAULT_BILLBOARD_CONFIG
from ..runner import run_spider
from ..spiders.billboard import BillboardSpider


class BillboardProvider(BaseProvider):
    """Billboard chart data provider (Scrapy-based)"""

    CHART_URLS = BillboardSpider.CHART_URLS
    ALBUM_CHARTS = BillboardSpider.ALBUM_CHARTS
    CHART_TITLES = BillboardSpider.CHART_TITLES

    def __init__(self, config: Optional[BillboardConfig] = None):
        """Initialize Billboard provider

        Args:
            config: Billboard-specific configuration
        """
        if config:
            self.config = {**DEFAULT_BILLBOARD_CONFIG, **config}
        else:
            self.config = DEFAULT_BILLBOARD_CONFIG.copy()
        self._setup()

    def _setup(self) -> None:
        """Prepare Scrapy settings from provider config"""
        self._scrapy_settings = {}

        timeout = self.config.get("timeout", 30)
        self._scrapy_settings["DOWNLOAD_TIMEOUT"] = timeout

        max_retries = self.config.get("max_retries", 3)
        self._scrapy_settings["RETRY_TIMES"] = max_retries

        user_agent = self.config.get("user_agent", "")
        if user_agent:
            self._scrapy_settings["USER_AGENT"] = user_agent

        verify_ssl = self.config.get("verify_ssl", True)
        if not verify_ssl:
            self._scrapy_settings["DOWNLOAD_HANDLERS_BASE"] = {}

        proxy = self.config.get("proxy")
        if proxy:
            self._scrapy_settings["HTTPPROXY_ENABLED"] = True
            self._scrapy_settings["HTTP_PROXY"] = proxy

    @property
    def name(self) -> str:
        return "billboard"

    @property
    def capabilities(self) -> ProviderCapability:
        return ProviderCapability.LATEST | ProviderCapability.LIST_CHARTS

    def _normalize_chart_name(self, chart_name: str) -> str:
        """Normalize chart name to URL path"""
        name_lower = chart_name.lower().strip()

        if name_lower in self.CHART_URLS:
            return name_lower

        normalized = name_lower.replace(" ", "-").replace("_", "-")
        if normalized in self.CHART_URLS:
            return normalized

        fallback_map = {
            "hot 100": "hot-100",
            "billboard hot 100": "hot-100",
            "200": "billboard-200",
            "billboard 200": "billboard-200",
            "global": "global-200",
            "artist": "artist-100",
        }

        if name_lower in fallback_map:
            return fallback_map[name_lower]

        if self.config.get("fallback_to_default", True):
            warnings.warn(
                f"Chart '{chart_name}' not found, falling back to hot-100"
            )
            return "hot-100"

        raise ValueError(
            f"Unknown chart: {chart_name}. "
            f"Available: {list(self.CHART_URLS.keys())}"
        )

    def _get_chart_type(self, chart_name: str) -> str:
        normalized = self._normalize_chart_name(chart_name)
        if normalized in self.ALBUM_CHARTS:
            return "album"
        return "single"

    def _assemble_chart(self, raw_item: dict) -> Chart:
        """Convert raw spider output to Chart model"""
        chart_type = raw_item.get("chart_type", "single")
        entries = []

        for raw_entry in raw_item.get("entries", []):
            entry_type = raw_entry.get("entry_type", "song")
            artist = raw_entry.get("artist", "")
            artists = raw_entry.get("artists", [artist] if artist else [])

            if entry_type == "album":
                album = Album(
                    title=raw_entry.get("title", ""),
                    artist=artists[0] if artists else artist,
                    artists=artists,
                    image=raw_entry.get("image", ""),
                )
                entry = ChartEntry(
                    album=album,
                    rank=raw_entry.get("rank", 0),
                    weeks_on_chart=raw_entry.get("weeks_on_chart", 0),
                    last_week=raw_entry.get("last_week", 0),
                    peak_position=raw_entry.get("peak_position", 0),
                )
            else:
                song = Song(
                    title=raw_entry.get("title", ""),
                    artist=artists[0] if artists else artist,
                    artists=artists,
                    image=raw_entry.get("image", ""),
                )
                entry = ChartEntry(
                    song=song,
                    rank=raw_entry.get("rank", 0),
                    weeks_on_chart=raw_entry.get("weeks_on_chart", 0),
                    last_week=raw_entry.get("last_week", 0),
                    peak_position=raw_entry.get("peak_position", 0),
                )
            entries.append(entry)

        entries.sort(key=lambda x: x.rank)

        metadata = ChartMetadata(
            provider="billboard",
            title=raw_item.get("chart_title", ""),
            description=raw_item.get("description", ""),
            url=raw_item.get("url", ""),
            type=chart_type,
        )

        return Chart(
            metadata=metadata,
            published_date=raw_item["published_date"],
            entries=entries,
            chart_type=chart_type,
        )

    def get_latest(self, chart_name: str, **kwargs) -> Chart:
        """Get the latest chart data using Scrapy spider

        Args:
            chart_name: Chart name (e.g., 'hot-100', 'billboard-200')

        Returns:
            Chart object with complete data
        """
        normalized = self._normalize_chart_name(chart_name)

        spider_kwargs = {
            "chart_name": normalized,
            "include_images": self.config.get("include_images", True),
        }

        max_entries = self.config.get("max_chart_entries")
        if max_entries is not None:
            spider_kwargs["max_chart_entries"] = max_entries

        try:
            results = run_spider(
                BillboardSpider,
                settings_override=self._scrapy_settings,
                **spider_kwargs,
            )
        except Exception as e:
            raise Exception(
                f"Failed to fetch Billboard chart: {str(e)}"
            ) from e

        if not results:
            raise Exception(
                f"Failed to fetch Billboard chart: no data returned for "
                f"'{normalized}'"
            )

        return self._assemble_chart(results[0])

    def get_chart(self, chart_name: str, chart_date: date, **kwargs) -> Chart:
        """Billboard doesn't support historical data via web scraping"""
        raise NotImplementedError(
            "Billboard provider doesn't support historical chart data. "
            "Only the latest charts are available via web scraping."
        )

    def list_available_charts(self) -> list[ChartMetadata]:
        """List all available charts"""
        charts = []

        chart_info = {
            "hot-100": (
                "Billboard Hot 100",
                "The week's most popular songs across all genres",
            ),
            "billboard-200": (
                "Billboard 200",
                "The week's most popular albums across all genres",
            ),
            "global-200": (
                "Global 200",
                "The week's most popular songs globally",
            ),
            "artist-100": (
                "Artist 100",
                "The week's most popular artists",
            ),
            "streaming-songs": (
                "Streaming Songs",
                "The most-streamed songs of the week",
            ),
            "radio-songs": (
                "Radio Songs",
                "The most-played songs on radio",
            ),
            "digital-song-sales": (
                "Digital Song Sales",
                "The best-selling digital songs",
            ),
        }

        for chart_id, (title, desc) in chart_info.items():
            path = self.CHART_URLS.get(chart_id, "")
            chart_type = self._get_chart_type(chart_id)
            charts.append(
                ChartMetadata(
                    provider=self.name,
                    title=title,
                    description=desc,
                    url=f"{BillboardSpider.BASE_URL}{path}",
                    type=chart_type,
                )
            )

        return charts

    def close(self) -> None:
        """No persistent resources to clean up with Scrapy-based approach"""
        pass
