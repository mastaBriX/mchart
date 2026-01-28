"""Data model definitions

Uses Pydantic for internal data validation but provides convenient JSON serialization.
Developers can work with dicts directly or use Pydantic models for type-safe operations.
"""

from datetime import date
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


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


class Album(BaseModel):
    """Album information"""
    
    title: str = Field(description="Album title")
    artist: str = Field(description="Primary artist")
    artists: list[str] = Field(default_factory=list, description="List of all artists")
    image: str = Field(default="", description="Cover image URL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Midnights",
                "artist": "Taylor Swift",
                "artists": ["Taylor Swift"],
                "image": "https://example.com/cover.jpg"
            }
        }
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format for JSON serialization"""
        return self.model_dump()


class ChartEntry(BaseModel):
    """Chart entry/position
    
    For single charts, use 'song' field.
    For album charts, use 'album' field.
    """
    
    song: Optional[Song] = Field(default=None, description="Song information (for single charts)")
    album: Optional[Album] = Field(default=None, description="Album information (for album charts)")
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
    
    @model_validator(mode='after')
    def validate_song_or_album(self) -> 'ChartEntry':
        """Validate that either song or album is provided, but not both"""
        if not self.song and not self.album:
            raise ValueError("ChartEntry must have either 'song' or 'album' field")
        if self.song and self.album:
            raise ValueError("ChartEntry cannot have both 'song' and 'album' fields")
        return self
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format, excluding None values for cleaner JSON"""
        # Use exclude_none to remove None values from output
        return self.model_dump(exclude_none=True)


class ChartMetadata(BaseModel):
    """Chart metadata"""
    
    provider: str = Field(description="Data source provider")
    title: str = Field(description="Chart title")
    description: str = Field(default="", description="Chart description")
    url: str = Field(default="", description="Original chart URL")
    type: Literal["single", "album"] = Field(default="single", description="Whether the chart is for singles or albums")
    
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
    chart_type: Literal["single", "album"] = Field(default="single", description="Chart type: 'single' for single/song charts, 'album' for album charts")
    
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
                "chart_type": "single",
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
        # Convert entries using their to_dict method to exclude None values
        data["entries"] = [entry.to_dict() for entry in self.entries]
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
        results = []
        for entry in self.entries:
            if entry.song:
                if (artist_lower in entry.song.artist.lower() or
                    any(artist_lower in a.lower() for a in entry.song.artists)):
                    results.append(entry)
            elif entry.album:
                if (artist_lower in entry.album.artist.lower() or
                    any(artist_lower in a.lower() for a in entry.album.artists)):
                    results.append(entry)
        return results
    
    def find_by_title(self, title: str) -> list[ChartEntry]:
        """Find entries by title (case-insensitive, supports partial match)
        
        Works for both song titles (single charts) and album titles (album charts).
        """
        title_lower = title.lower()
        results = []
        for entry in self.entries:
            if entry.song and title_lower in entry.song.title.lower():
                results.append(entry)
            elif entry.album and title_lower in entry.album.title.lower():
                results.append(entry)
        return results
