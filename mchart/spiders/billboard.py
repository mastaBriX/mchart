"""Billboard chart spider

Scrapes chart data from billboard.com using Scrapy.
"""

import re
from datetime import date

import scrapy

from ..items import ChartPageItem


class BillboardSpider(scrapy.Spider):
    """Spider for scraping Billboard chart pages"""

    name = "billboard"
    allowed_domains = ["billboard.com"]

    BASE_URL = "https://www.billboard.com"

    CHART_URLS = {
        "hot-100": "/charts/hot-100",
        "billboard-200": "/charts/billboard-200",
        "global-200": "/charts/global-200",
        "artist-100": "/charts/artist-100",
        "streaming-songs": "/charts/streaming-songs",
        "radio-songs": "/charts/radio-songs",
        "digital-song-sales": "/charts/digital-song-sales",
    }

    ALBUM_CHARTS = {"billboard-200"}

    CHART_TITLES = {
        "hot-100": "Billboard Hot 100",
        "billboard-200": "Billboard 200",
        "global-200": "Global 200",
        "artist-100": "Artist 100",
        "streaming-songs": "Streaming Songs",
        "radio-songs": "Radio Songs",
        "digital-song-sales": "Digital Song Sales",
    }

    FALLBACK_DESCRIPTIONS = {
        "hot-100": (
            "The week's most popular songs across all genres, "
            "ranked by radio airplay, sales data, and streaming activity."
        ),
        "billboard-200": (
            "The week's most popular albums across all genres, "
            "ranked by album sales and audio streaming."
        ),
        "global-200": (
            "The week's most popular songs globally, "
            "ranked by streaming and sales activity."
        ),
    }

    def __init__(self, chart_name="hot-100", include_images=True,
                 max_chart_entries=None, **kwargs):
        super().__init__(**kwargs)
        self.chart_name = chart_name
        self.include_images = include_images
        self.max_chart_entries = (
            int(max_chart_entries) if max_chart_entries else None
        )

    def start_requests(self):
        path = self.CHART_URLS.get(self.chart_name, self.CHART_URLS["hot-100"])
        url = f"{self.BASE_URL}{path}"
        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={"chart_name": self.chart_name},
        )

    def parse(self, response):
        chart_name = response.meta["chart_name"]
        chart_type = "album" if chart_name in self.ALBUM_CHARTS else "single"

        # Parse publication date
        published_date = self._parse_date(response)

        # Parse entries
        if chart_type == "album":
            entries = self._parse_album_entries(response)
        else:
            entries = self._parse_entries(response)

        # Get description
        description = self._parse_description(response, chart_name)

        chart_title = self.CHART_TITLES.get(chart_name, chart_name)

        item = ChartPageItem(
            provider="billboard",
            chart_name=chart_name,
            chart_title=chart_title,
            chart_type=chart_type,
            description=description,
            url=response.url,
            published_date=published_date,
            entries=entries,
        )
        yield item

    def _parse_date(self, response):
        """Parse publication date from page"""
        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }

        # Search for date text in the page
        body_text = response.text
        date_matches = re.findall(
            r"Week of\s+(\w+)\s+(\d{1,2}),\s+(\d{4})",
            body_text,
            re.IGNORECASE,
        )
        if date_matches:
            month_name, day, year = date_matches[0]
            month = month_map.get(month_name.lower())
            if month:
                return date(int(year), month, int(day))

        # Format: "Week of M/D/YYYY"
        date_matches = re.findall(
            r"Week of\s+(\d{1,2})/(\d{1,2})/(\d{4})",
            body_text,
        )
        if date_matches:
            month, day, year = date_matches[0]
            return date(int(year), int(month), int(day))

        return date.today()

    def _parse_entries(self, response):
        """Parse single chart entries"""
        entries = []
        rows = response.css("ul.o-chart-results-list-row")

        for row in rows:
            entry = self._parse_single_row(row)
            if entry:
                entries.append(entry)
                if self.max_chart_entries and len(entries) >= self.max_chart_entries:
                    break

        entries.sort(key=lambda x: x["rank"])
        return entries

    def _parse_album_entries(self, response):
        """Parse album chart entries"""
        entries = []
        rows = response.css("ul.o-chart-results-list-row")

        for row in rows:
            entry = self._parse_album_row(row)
            if entry:
                entries.append(entry)
                if self.max_chart_entries and len(entries) >= self.max_chart_entries:
                    break

        entries.sort(key=lambda x: x["rank"])
        return entries

    def _parse_single_row(self, row):
        """Parse a single chart row into a dict"""
        rank = self._extract_rank(row)
        if rank == 0:
            return None

        title = self._extract_title(row)
        if not title:
            return None

        artist = self._extract_artist(row, title, is_album_chart=False)
        if not artist:
            return None

        artists = self._split_artists(artist)
        image = self._extract_image(row) if self.include_images else ""
        weeks_on_chart = self._extract_weeks(row)
        last_week = self._extract_last_week(row)
        peak_position = self._extract_peak(row, rank)

        return {
            "rank": rank,
            "title": title,
            "artist": artists[0] if artists else artist,
            "artists": artists,
            "image": image,
            "weeks_on_chart": weeks_on_chart,
            "last_week": last_week,
            "peak_position": peak_position,
            "entry_type": "song",
        }

    def _parse_album_row(self, row):
        """Parse an album chart row into a dict"""
        rank = self._extract_rank(row)
        if rank == 0:
            return None

        title = self._extract_title(row)
        if not title:
            return None

        artist = self._extract_artist(row, title, is_album_chart=True)
        if not artist:
            return None

        artists = self._split_artists(artist)
        image = self._extract_image(row) if self.include_images else ""
        weeks_on_chart = self._extract_weeks(row)
        last_week = self._extract_last_week(row)
        peak_position = self._extract_peak(row, rank)

        return {
            "rank": rank,
            "title": title,
            "artist": artists[0] if artists else artist,
            "artists": artists,
            "image": image,
            "weeks_on_chart": weeks_on_chart,
            "last_week": last_week,
            "peak_position": peak_position,
            "entry_type": "album",
        }

    def _extract_rank(self, row):
        """Extract rank number from row"""
        spans = row.css("span.c-label::text").getall()
        for text in spans:
            text = text.strip()
            if text.isdigit():
                return int(text)
        return 0

    def _extract_title(self, row):
        """Extract song/album title from row"""
        title_elem = row.css("h3.c-title::text").get()
        return title_elem.strip() if title_elem else ""

    def _extract_artist(self, row, title, is_album_chart=False):
        """Extract artist name from row"""
        artist = ""

        # Method 1: Find in links containing /artist/
        for link in row.css("a"):
            href = link.attrib.get("href", "")
            text = link.css("::text").get()
            if text:
                text = text.strip()
            if "/artist/" in href and text:
                if is_album_chart:
                    if not artist:
                        artist = text
                    else:
                        artist += f" & {text}"
                else:
                    if text != title:
                        if not artist:
                            artist = text
                        else:
                            artist += f" & {text}"

        # Method 2: Find in span.c-label (excluding rank)
        if not artist:
            for span in row.css("span.c-label"):
                text = span.css("::text").get()
                if not text:
                    continue
                text = re.sub(r"\s+", " ", text).strip()

                if (text and not text.isdigit() and text != title
                        and 2 < len(text) < 150):
                    text_upper = text.upper().strip()
                    if text_upper in ["NEW", "RE-ENTRY", "RE-\nENTRY", "-", ""]:
                        continue

                    parent_is_link = span.xpath("ancestor::a")
                    if parent_is_link:
                        artist = text
                        break
                    elif ("&" in text or "," in text or len(text) > 8
                          or (text and text[0].isupper())):
                        if not artist:
                            artist = text

        return artist

    def _extract_image(self, row):
        """Extract cover image URL"""
        img = row.css("img")
        if img:
            for attr in ["data-lazy-src", "data-src", "data-original", "src"]:
                url = img.attrib.get(attr, "")
                if url and "lazyload-fallback" not in url and url.startswith("http"):
                    return url
        return ""

    def _extract_weeks(self, row):
        """Extract weeks on chart"""
        row_text = row.get()
        weeks_match = re.search(r"(\d+)\s+weeks?", row_text, re.IGNORECASE)
        if weeks_match:
            return int(weeks_match.group(1))
        return 0

    def _extract_last_week(self, row):
        """Extract last week's rank"""
        row_text = row.css("::text").getall()
        full_text = " ".join(row_text)
        lw_match = re.search(r"LW[:\s]*(\d+)", full_text, re.IGNORECASE)
        if lw_match:
            return int(lw_match.group(1))
        return 0

    def _extract_peak(self, row, current_rank):
        """Extract peak position"""
        row_text = row.css("::text").getall()
        full_text = " ".join(row_text)
        peak_match = re.search(r"Peak[:\s]*(\d+)", full_text, re.IGNORECASE)
        if peak_match:
            return int(peak_match.group(1))
        return current_rank

    def _split_artists(self, artist):
        """Split artist string into list"""
        if "&" in artist:
            return [a.strip() for a in artist.split("&")]
        elif "," in artist:
            return [a.strip() for a in artist.split(",")]
        return [artist]

    def _parse_description(self, response, chart_name):
        """Extract description from meta tag or use fallback"""
        meta_desc = response.css('meta[name="description"]::attr(content)').get()
        if meta_desc:
            return meta_desc.strip()

        return self.FALLBACK_DESCRIPTIONS.get(
            chart_name,
            f"The {chart_name} chart on Billboard",
        )
