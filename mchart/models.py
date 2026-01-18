"""Data model definitions

Uses Pydantic for internal data validation but provides convenient JSON serialization.
Developers can work with dicts directly or use Pydantic models for type-safe operations.
"""

from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class Song(BaseModel):
    """Song information"""
    
    title: str = Field(description="Song title")
    artist: str = Field(description="Primary artist")
    artists: list[str] = Field(default_factory=list, description="List of all artists")
    image: str = Field(default="", description="Cover image URL")
    album: str = Field(default="", description="Album name")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Anti-Hero",
                "artist": "Taylor Swift",
                "artists": ["Taylor Swift"],
                "image": "https://example.com/cover.jpg",
                "album": "Midnights"
            }
        }
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format for JSON serialization"""
        return self.model_dump()


class ChartEntry(BaseModel):
    """Chart entry/position"""
    
    song: Song = Field(description="Song information")
    rank: int = Field(description="Current rank")
    weeks_on_chart: int = Field(default=0, description="Number of weeks on chart")
    last_week: int = Field(default=0, description="Last week's rank, 0 means new entry or no data")
    peak_position: int = Field(default=0, description="Peak position in history")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "song": {
                    "title": "Anti-Hero",
                    "artist": "Taylor Swift",
                    "artists": ["Taylor Swift"],
                    "image": "https://example.com/cover.jpg",
                    "album": "Midnights"
                },
                "rank": 1,
                "weeks_on_chart": 5,
                "last_week": 2,
                "peak_position": 1
            }
        }
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format"""
        return self.model_dump()


class ChartMetadata(BaseModel):
    """Chart metadata"""
    
    provider: str = Field(description="Data source provider")
    title: str = Field(description="Chart title")
    description: str = Field(default="", description="Chart description")
    url: str = Field(default="", description="Original chart URL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "billboard",
                "title": "Billboard Hot 100",
                "description": "The week's most popular songs across all genres...",
                "url": "https://www.billboard.com/charts/hot-100"
            }
        }
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format"""
        return self.model_dump()


class Chart(BaseModel):
    """Complete chart data"""
    
    metadata: ChartMetadata = Field(description="Chart metadata")
    published_date: date = Field(description="Publication date")
    entries: list[ChartEntry] = Field(default_factory=list, description="List of chart entries")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "provider": "billboard",
                    "title": "Billboard Hot 100",
                    "description": "The week's most popular songs...",
                    "url": "https://www.billboard.com/charts/hot-100"
                },
                "published_date": "2026-01-18",
                "entries": [
                    {
                        "song": {
                            "title": "Anti-Hero",
                            "artist": "Taylor Swift",
                            "artists": ["Taylor Swift"],
                            "image": "https://example.com/cover.jpg",
                            "album": "Midnights"
                        },
                        "rank": 1,
                        "weeks_on_chart": 5,
                        "last_week": 2,
                        "peak_position": 1
                    }
                ]
            }
        }
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format for JSON serialization
        
        Returns:
            Dict containing all data, dates are converted to ISO format strings
        """
        data = self.model_dump()
        # Ensure date is in string format
        data["published_date"] = self.published_date.isoformat()
        return data
    
    @property
    def total_entries(self) -> int:
        """Total number of chart entries"""
        return len(self.entries)
    
    def get_top(self, n: int = 10) -> list[ChartEntry]:
        """Get top N entries"""
        return self.entries[:n]
    
    def find_by_artist(self, artist: str) -> list[ChartEntry]:
        """Find entries by artist name (case-insensitive)"""
        artist_lower = artist.lower()
        return [
            entry for entry in self.entries
            if artist_lower in entry.song.artist.lower()
            or any(artist_lower in a.lower() for a in entry.song.artists)
        ]
    
    def find_by_title(self, title: str) -> list[ChartEntry]:
        """Find entries by song title (case-insensitive, supports partial match)"""
        title_lower = title.lower()
        return [
            entry for entry in self.entries
            if title_lower in entry.song.title.lower()
        ]
