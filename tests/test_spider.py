"""Tests for Billboard spider parsing logic using fake Scrapy responses"""

import pytest
from datetime import date
from scrapy.http import HtmlResponse, Request

from mchart.spiders.billboard import BillboardSpider


def _fake_response(url, body):
    """Create a fake Scrapy HtmlResponse for testing"""
    request = Request(url=url, meta={"chart_name": "hot-100"})
    return HtmlResponse(
        url=url,
        request=request,
        body=body.encode("utf-8"),
        encoding="utf-8",
    )


SAMPLE_HTML = """
<html>
<head>
<meta name="description" content="The week's most popular songs"/>
</head>
<body>
<p>Week of January 21, 2026</p>
<ul class="o-chart-results-list-row">
    <span class="c-label">1</span>
    <h3 class="c-title">Test Song One</h3>
    <a href="/music/artist/123"><span class="c-label">Artist Alpha</span></a>
    <img src="https://example.com/img1.jpg"/>
    <span>2 weeks</span>
    <span>LW: 3</span>
    <span>Peak: 1</span>
</ul>
<ul class="o-chart-results-list-row">
    <span class="c-label">2</span>
    <h3 class="c-title">Test Song Two</h3>
    <a href="/music/artist/456"><span class="c-label">Artist Beta</span></a>
    <img src="https://example.com/img2.jpg"/>
    <span>5 weeks</span>
    <span>LW: 1</span>
    <span>Peak: 1</span>
</ul>
</body>
</html>
"""

SAMPLE_ALBUM_HTML = """
<html>
<head>
<meta name="description" content="The week's most popular albums"/>
</head>
<body>
<p>Week of January 21, 2026</p>
<ul class="o-chart-results-list-row">
    <span class="c-label">1</span>
    <h3 class="c-title">Test Album</h3>
    <a href="/music/artist/789"><span class="c-label">Album Artist</span></a>
    <img src="https://example.com/album.jpg"/>
    <span>10 weeks</span>
</ul>
</body>
</html>
"""


class TestBillboardSpiderParsing:
    """Test spider parsing with fake HTML responses"""

    def test_parse_date(self):
        """Test date extraction from page"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        parsed_date = spider._parse_date(response)
        assert parsed_date == date(2026, 1, 21)

    def test_parse_date_fallback(self):
        """Test date extraction fallback to today"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            "<html><body>No date here</body></html>",
        )
        parsed_date = spider._parse_date(response)
        assert parsed_date == date.today()

    def test_parse_entries(self):
        """Test parsing single chart entries"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        entries = spider._parse_entries(response)
        assert len(entries) == 2

        assert entries[0]["rank"] == 1
        assert entries[0]["title"] == "Test Song One"
        assert entries[0]["entry_type"] == "song"

        assert entries[1]["rank"] == 2
        assert entries[1]["title"] == "Test Song Two"

    def test_parse_entries_max_limit(self):
        """Test that max_chart_entries limits results"""
        spider = BillboardSpider(max_chart_entries=1)
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        entries = spider._parse_entries(response)
        assert len(entries) == 1

    def test_parse_album_entries(self):
        """Test parsing album chart entries"""
        spider = BillboardSpider(chart_name="billboard-200")
        response = _fake_response(
            "https://www.billboard.com/charts/billboard-200",
            SAMPLE_ALBUM_HTML,
        )
        entries = spider._parse_album_entries(response)
        assert len(entries) == 1
        assert entries[0]["title"] == "Test Album"
        assert entries[0]["entry_type"] == "album"

    def test_parse_description(self):
        """Test description extraction from meta tag"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        desc = spider._parse_description(response, "hot-100")
        assert desc == "The week's most popular songs"

    def test_parse_description_fallback(self):
        """Test description fallback when no meta tag"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            "<html><body></body></html>",
        )
        desc = spider._parse_description(response, "hot-100")
        assert "most popular songs" in desc

    def test_full_parse(self):
        """Test full parse method produces ChartPageItem"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        response.meta["chart_name"] = "hot-100"

        items = list(spider.parse(response))
        assert len(items) == 1

        item = items[0]
        assert item["provider"] == "billboard"
        assert item["chart_title"] == "Billboard Hot 100"
        assert item["chart_type"] == "single"
        assert item["published_date"] == date(2026, 1, 21)
        assert len(item["entries"]) == 2

    def test_parse_no_images(self):
        """Test parsing with images disabled"""
        spider = BillboardSpider(include_images=False)
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            SAMPLE_HTML,
        )
        entries = spider._parse_entries(response)
        for entry in entries:
            assert entry["image"] == ""

    def test_parse_empty_page(self):
        """Test parsing empty page produces no entries"""
        spider = BillboardSpider()
        response = _fake_response(
            "https://www.billboard.com/charts/hot-100",
            "<html><body></body></html>",
        )
        entries = spider._parse_entries(response)
        assert entries == []
