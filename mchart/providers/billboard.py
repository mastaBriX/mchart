"""Billboard provider implementation

Scrapes chart data from billboard.com
"""

from datetime import date
from typing import Optional
import re
import warnings

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from .base import BaseProvider, ProviderCapability
from ..models import Chart, ChartEntry, ChartMetadata, Song
from ..config import BillboardConfig, DEFAULT_BILLBOARD_CONFIG


class BillboardProvider(BaseProvider):
    """Billboard chart data provider"""
    
    BASE_URL = "https://www.billboard.com"
    
    # Chart name to URL path mapping
    CHART_URLS = {
        "hot-100": "/charts/hot-100",
        "billboard-200": "/charts/billboard-200",
        "global-200": "/charts/global-200",
        "artist-100": "/charts/artist-100",
        "streaming-songs": "/charts/streaming-songs",
        "radio-songs": "/charts/radio-songs",
        "digital-song-sales": "/charts/digital-song-sales",
    }
    
    def __init__(self, config: Optional[BillboardConfig] = None):
        """
        Initialize Billboard provider
        
        Args:
            config: Billboard-specific configuration
        """
        # Merge user config with defaults
        if config:
            self.config = {**DEFAULT_BILLBOARD_CONFIG, **config}
        else:
            self.config = DEFAULT_BILLBOARD_CONFIG.copy()
        
        # Determine parser
        parser = self.config.get("parser", "lxml")
        try:
            if parser == "lxml":
                import lxml
                self.parser = "lxml"
            elif parser == "html5lib":
                import html5lib
                self.parser = "html5lib"
            else:
                self.parser = "html.parser"
        except ImportError:
            warnings.warn(f"{parser} is not installed, falling back to html.parser")
            self.parser = "html.parser"
        
        self._setup()
    
    def _setup(self) -> None:
        """Setup HTTP session with retry logic"""
        self.session = Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.get("max_retries", 3),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            "User-Agent": self.config.get("user_agent", ""),
        })
        
        # Set proxy if provided
        if self.config.get("proxy"):
            self.session.proxies = {
                "http": self.config["proxy"],
                "https": self.config["proxy"],
            }
    
    @property
    def name(self) -> str:
        """Provider name"""
        return "billboard"
    
    @property
    def capabilities(self) -> ProviderCapability:
        """Billboard only supports latest charts and listing"""
        return ProviderCapability.LATEST | ProviderCapability.LIST_CHARTS
    
    def _normalize_chart_name(self, chart_name: str) -> str:
        """Normalize chart name to URL path"""
        # Convert common names to URL paths
        name_lower = chart_name.lower().strip()
        
        # Direct mapping
        if name_lower in self.CHART_URLS:
            return name_lower
        
        # Try to match by removing spaces and hyphens
        normalized = name_lower.replace(" ", "-").replace("_", "-")
        if normalized in self.CHART_URLS:
            return normalized
        
        # Fallback mappings
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
        
        # If fallback is enabled, return hot-100
        if self.config.get("fallback_to_default", True):
            warnings.warn(
                f"Chart '{chart_name}' not found, falling back to hot-100"
            )
            return "hot-100"
        
        raise ValueError(
            f"Unknown chart: {chart_name}. Available: {list(self.CHART_URLS.keys())}"
        )
    
    def _get_chart_url(self, chart_name: str) -> str:
        """Get full URL for a chart"""
        normalized = self._normalize_chart_name(chart_name)
        path = self.CHART_URLS.get(normalized, self.CHART_URLS["hot-100"])
        return f"{self.BASE_URL}{path}"
    
    def _parse_date(self, soup: BeautifulSoup) -> date:
        """Parse publication date from page"""
        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        
        # Find date in page
        date_elements = soup.find_all(string=re.compile(r"Week of", re.IGNORECASE))
        if date_elements:
            date_text = date_elements[0].strip()
            
            # Format: "Week of January 10, 2026"
            match = re.search(
                r"Week of\s+(\w+)\s+(\d{1,2}),\s+(\d{4})",
                date_text,
                re.IGNORECASE
            )
            if match:
                month_name, day, year = match.groups()
                month = month_map.get(month_name.lower())
                if month:
                    return date(int(year), month, int(day))
            
            # Format: "Week of 1/10/2026"
            match = re.search(r"Week of\s+(\d{1,2})/(\d{1,2})/(\d{4})", date_text)
            if match:
                month, day, year = match.groups()
                return date(int(year), int(month), int(day))
        
        # Fallback to today
        return date.today()
    
    def _parse_entries(self, soup: BeautifulSoup) -> list[ChartEntry]:
        """Parse chart entries from HTML"""
        entries = []
        include_images = self.config.get("include_images", True)
        max_entries = self.config.get("max_chart_entries")
        
        # Find all chart rows
        chart_rows = soup.find_all("ul", class_=re.compile(r"o-chart-results-list-row"))
        
        for row in chart_rows:
            try:
                # Extract rank
                rank = 0
                rank_elem = row.find("span", class_=re.compile(r"c-label"))
                if rank_elem:
                    rank_text = rank_elem.get_text(strip=True)
                    if rank_text.isdigit():
                        rank = int(rank_text)
                
                if rank == 0:
                    continue
                
                # Extract song title
                title_elem = row.find("h3", class_=re.compile(r"c-title"))
                song_title = title_elem.get_text(strip=True) if title_elem else ""
                
                if not song_title:
                    continue
                
                # Extract artist
                artist = self._extract_artist(row, song_title)
                if not artist:
                    continue
                
                # Extract image URL
                image_url = ""
                if include_images:
                    image_url = self._extract_image(row)
                
                # Parse multiple artists
                if "&" in artist:
                    artists = [a.strip() for a in artist.split("&")]
                elif "," in artist:
                    artists = [a.strip() for a in artist.split(",")]
                else:
                    artists = [artist]
                
                # Extract additional data
                weeks_on_chart = self._extract_weeks(row)
                last_week = self._extract_last_week(row)
                peak_position = self._extract_peak(row, rank)
                
                # Create entry
                song = Song(
                    title=song_title,
                    artist=artists[0] if artists else artist,
                    artists=artists,
                    image=image_url,
                    album=""
                )
                
                entry = ChartEntry(
                    song=song,
                    rank=rank,
                    weeks_on_chart=weeks_on_chart,
                    last_week=last_week,
                    peak_position=peak_position
                )
                
                entries.append(entry)
                
                # Check if we've reached the limit
                if max_entries and len(entries) >= max_entries:
                    break
                
            except Exception:
                # Skip failed entries
                continue
        
        # Sort by rank
        entries.sort(key=lambda x: x.rank)
        return entries
    
    def _extract_artist(self, row, song_title: str) -> str:
        """Extract artist name from row"""
        artist = ""
        
        # Method 1: Find in links containing /artist/
        links = row.find_all("a")
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if "/artist/" in href and text and text != song_title:
                if not artist:
                    artist = text
                else:
                    artist += f" & {text}"
        
        # Method 2: Find in span.c-label (excluding rank)
        if not artist:
            all_spans = row.find_all("span", class_=re.compile(r"c-label"))
            candidates = []
            
            for span in all_spans:
                text = span.get_text(strip=True)
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Filter conditions
                if (text and not text.isdigit() and text != song_title and 
                    2 < len(text) < 150):
                    
                    # Exclude special markers
                    text_upper = text.upper().strip()
                    if text_upper in ["NEW", "RE-ENTRY", "RE-\nENTRY", "-", ""]:
                        continue
                    
                    # Prefer text in links
                    parent_link = span.find_parent("a")
                    if parent_link:
                        candidates.insert(0, text)
                    elif ("&" in text or "," in text or len(text) > 8 or 
                          (text and text[0].isupper())):
                        candidates.append(text)
            
            if candidates:
                artist = candidates[0]
        
        return artist
    
    def _extract_image(self, row) -> str:
        """Extract cover image URL"""
        img_elem = row.find("img")
        if img_elem:
            for attr in ["data-lazy-src", "data-src", "data-original", "src"]:
                url = img_elem.get(attr, "")
                if url and "lazyload-fallback" not in url and url.startswith("http"):
                    return url
        return ""
    
    def _extract_weeks(self, row) -> int:
        """Extract weeks on chart"""
        weeks_text = row.find(string=re.compile(r"\d+\s+weeks?"))
        if weeks_text:
            weeks_match = re.search(r"(\d+)", weeks_text)
            if weeks_match:
                return int(weeks_match.group(1))
        return 0
    
    def _extract_last_week(self, row) -> int:
        """Extract last week's rank"""
        lw_span = row.find("span", string=re.compile(r"LW", re.IGNORECASE))
        if lw_span:
            # Method 1: Check next sibling
            next_sibling = lw_span.find_next_sibling()
            if next_sibling:
                text = next_sibling.get_text(strip=True)
                if text.isdigit():
                    return int(text)
            
            # Method 2: Search in parent
            if lw_span.parent:
                parent_spans = lw_span.parent.find_all(
                    "span", class_=re.compile(r"c-label")
                )
                for span in parent_spans:
                    text = span.get_text(strip=True)
                    if text.isdigit() and span != lw_span:
                        return int(text)
        
        # Method 3: Regex in entire row
        row_text = row.get_text()
        lw_match = re.search(r"LW[:\s]*(\d+)", row_text, re.IGNORECASE)
        if lw_match:
            return int(lw_match.group(1))
        
        return 0
    
    def _extract_peak(self, row, current_rank: int) -> int:
        """Extract peak position"""
        peak_text = row.find(string=re.compile(r"Peak.*?\d+"))
        if peak_text:
            peak_match = re.search(r"Peak.*?(\d+)", peak_text)
            if peak_match:
                return int(peak_match.group(1))
        
        # Try regex in entire row
        row_text = row.get_text()
        peak_match = re.search(r"Peak[:\s]*(\d+)", row_text, re.IGNORECASE)
        if peak_match:
            return int(peak_match.group(1))
        
        # Default to current rank
        return current_rank
    
    def get_latest(self, chart_name: str, **kwargs) -> Chart:
        """
        Get the latest chart data
        
        Args:
            chart_name: Chart name (e.g., 'hot-100', 'billboard-200')
            **kwargs: Additional options (unused)
            
        Returns:
            Chart object with complete data
        """
        url = self._get_chart_url(chart_name)
        
        try:
            response = self.session.get(
                url,
                timeout=self.config.get("timeout", 30),
                verify=self.config.get("verify_ssl", True)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, self.parser)
            
            # Parse data
            published_date = self._parse_date(soup)
            entries = self._parse_entries(soup)
            
            # Get description from meta tag
            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                description = meta_desc.get("content", "").strip()
            
            # Fallback descriptions
            if not description:
                desc_map = {
                    "hot-100": "The week's most popular songs across all genres, ranked by radio airplay, sales data, and streaming activity.",
                    "billboard-200": "The week's most popular albums across all genres, ranked by album sales and audio streaming.",
                    "global-200": "The week's most popular songs globally, ranked by streaming and sales activity.",
                }
                normalized = self._normalize_chart_name(chart_name)
                description = desc_map.get(normalized, f"The {chart_name} chart on Billboard")
            
            # Create chart metadata
            metadata = ChartMetadata(
                provider=self.name,
                title=chart_name,
                description=description,
                url=url
            )
            
            return Chart(
                metadata=metadata,
                published_date=published_date,
                entries=entries
            )
            
        except Exception as e:
            raise Exception(f"Failed to fetch Billboard chart: {str(e)}") from e
    
    def get_chart(self, chart_name: str, chart_date: date, **kwargs) -> Chart:
        """
        Billboard doesn't support historical data via web scraping
        
        Raises:
            NotImplementedError: Always, as historical data is not supported
        """
        raise NotImplementedError(
            "Billboard provider doesn't support historical chart data. "
            "Only the latest charts are available via web scraping."
        )
    
    def list_available_charts(self) -> list[ChartMetadata]:
        """
        List all available charts
        
        Returns:
            List of available chart metadata
        """
        charts = []
        
        # Chart descriptions
        chart_info = {
            "hot-100": ("Billboard Hot 100", "The week's most popular songs across all genres"),
            "billboard-200": ("Billboard 200", "The week's most popular albums across all genres"),
            "global-200": ("Global 200", "The week's most popular songs globally"),
            "artist-100": ("Artist 100", "The week's most popular artists"),
            "streaming-songs": ("Streaming Songs", "The most-streamed songs of the week"),
            "radio-songs": ("Radio Songs", "The most-played songs on radio"),
            "digital-song-sales": ("Digital Song Sales", "The best-selling digital songs"),
        }
        
        for chart_id, (title, desc) in chart_info.items():
            path = self.CHART_URLS.get(chart_id, "")
            charts.append(ChartMetadata(
                provider=self.name,
                title=title,
                description=desc,
                url=f"{self.BASE_URL}{path}"
            ))
        
        return charts
    
    def close(self) -> None:
        """Close HTTP session"""
        if hasattr(self, 'session'):
            self.session.close()
