"""Tests for data models"""

import pytest
from datetime import date
from pydantic import ValidationError

from mchart.models import Song, Album, ChartEntry, ChartMetadata, Chart


class TestSong:
    """Tests for Song model"""
    
    def test_song_creation(self):
        """Test creating a song"""
        song = Song(
            title="Test Song",
            artist="Test Artist",
            artists=["Test Artist"],
            image="https://example.com/image.jpg",
            album="Test Album"
        )
        assert song.title == "Test Song"
        assert song.artist == "Test Artist"
        assert song.artists == ["Test Artist"]
        assert song.image == "https://example.com/image.jpg"
        assert song.album == "Test Album"
    
    def test_song_minimal(self):
        """Test creating a song with minimal fields"""
        song = Song(title="Test", artist="Artist")
        assert song.title == "Test"
        assert song.artist == "Artist"
        assert song.artists == []
        assert song.image == ""
        assert song.album == ""
    
    def test_song_to_dict(self):
        """Test converting song to dict"""
        song = Song(title="Test", artist="Artist")
        data = song.to_dict()
        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["artist"] == "Artist"


class TestAlbum:
    """Tests for Album model"""
    
    def test_album_creation(self):
        """Test creating an album"""
        album = Album(
            title="Test Album",
            artist="Test Artist",
            artists=["Test Artist"],
            image="https://example.com/image.jpg"
        )
        assert album.title == "Test Album"
        assert album.artist == "Test Artist"
        assert album.artists == ["Test Artist"]
        assert album.image == "https://example.com/image.jpg"
    
    def test_album_minimal(self):
        """Test creating an album with minimal fields"""
        album = Album(title="Test", artist="Artist")
        assert album.title == "Test"
        assert album.artist == "Artist"
        assert album.artists == []
        assert album.image == ""
    
    def test_album_to_dict(self):
        """Test converting album to dict"""
        album = Album(title="Test", artist="Artist")
        data = album.to_dict()
        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["artist"] == "Artist"


class TestChartEntry:
    """Tests for ChartEntry model"""
    
    def test_single_entry_creation(self, sample_song):
        """Test creating a single chart entry"""
        entry = ChartEntry(
            song=sample_song,
            rank=1,
            weeks_on_chart=5,
            last_week=2,
            peak_position=1
        )
        assert entry.song == sample_song
        assert entry.album is None
        assert entry.rank == 1
        assert entry.weeks_on_chart == 5
    
    def test_album_entry_creation(self, sample_album):
        """Test creating an album chart entry"""
        entry = ChartEntry(
            album=sample_album,
            rank=1,
            weeks_on_chart=3,
            last_week=0,
            peak_position=1
        )
        assert entry.album == sample_album
        assert entry.song is None
        assert entry.rank == 1
    
    def test_entry_validation_no_song_or_album(self):
        """Test that entry must have either song or album"""
        with pytest.raises(ValidationError):
            ChartEntry(rank=1)
    
    def test_entry_validation_both_song_and_album(self, sample_song, sample_album):
        """Test that entry cannot have both song and album"""
        with pytest.raises(ValidationError):
            ChartEntry(song=sample_song, album=sample_album, rank=1)
    
    def test_entry_to_dict_excludes_none(self, sample_song):
        """Test that to_dict excludes None values"""
        entry = ChartEntry(song=sample_song, rank=1)
        data = entry.to_dict()
        assert "song" in data
        assert "album" not in data  # Should be excluded if None


class TestChartMetadata:
    """Tests for ChartMetadata model"""
    
    def test_metadata_creation(self):
        """Test creating metadata"""
        metadata = ChartMetadata(
            provider="billboard",
            title="Test Chart",
            description="Test description",
            url="https://example.com",
            type="single"
        )
        assert metadata.provider == "billboard"
        assert metadata.title == "Test Chart"
        assert metadata.type == "single"
    
    def test_metadata_defaults(self):
        """Test metadata with defaults"""
        metadata = ChartMetadata(provider="billboard", title="Test")
        assert metadata.description == ""
        assert metadata.url == ""
        assert metadata.type == "single"  # Default
    
    def test_metadata_type_validation(self):
        """Test that type must be 'single' or 'album'"""
        # Valid types
        ChartMetadata(provider="billboard", title="Test", type="single")
        ChartMetadata(provider="billboard", title="Test", type="album")
        
        # Invalid type
        with pytest.raises(ValidationError):
            ChartMetadata(provider="billboard", title="Test", type="invalid")


class TestChart:
    """Tests for Chart model"""
    
    def test_chart_creation(self, sample_single_metadata, sample_single_entry):
        """Test creating a chart"""
        chart = Chart(
            metadata=sample_single_metadata,
            published_date=date(2026, 1, 21),
            entries=[sample_single_entry]
        )
        assert chart.metadata == sample_single_metadata
        assert chart.published_date == date(2026, 1, 21)
        assert len(chart.entries) == 1
    
    def test_chart_total_entries(self, sample_single_chart):
        """Test total_entries property"""
        assert sample_single_chart.total_entries == 1
    
    def test_chart_get_top(self, sample_single_metadata, sample_song):
        """Test get_top method"""
        entries = [
            ChartEntry(song=sample_song, rank=i, weeks_on_chart=1)
            for i in range(1, 11)
        ]
        chart = Chart(
            metadata=sample_single_metadata,
            published_date=date(2026, 1, 21),
            entries=entries
        )
        top_5 = chart.get_top(5)
        assert len(top_5) == 5
        assert top_5[0].rank == 1
    
    def test_chart_find_by_artist_single(self, sample_single_chart, sample_song):
        """Test find_by_artist for single chart"""
        results = sample_single_chart.find_by_artist("Test Artist")
        assert len(results) == 1
        assert results[0].song.artist == "Test Artist"
    
    def test_chart_find_by_artist_album(self, sample_album_chart):
        """Test find_by_artist for album chart"""
        results = sample_album_chart.find_by_artist("Test Artist")
        assert len(results) == 1
        assert results[0].album.artist == "Test Artist"
    
    def test_chart_find_by_title_single(self, sample_single_chart):
        """Test find_by_title for single chart"""
        results = sample_single_chart.find_by_title("Test Song")
        assert len(results) == 1
        assert results[0].song.title == "Test Song"
    
    def test_chart_find_by_title_album(self, sample_album_chart):
        """Test find_by_title for album chart"""
        results = sample_album_chart.find_by_title("Test Album")
        assert len(results) == 1
        assert results[0].album.title == "Test Album"
    
    def test_chart_to_dict(self, sample_single_chart):
        """Test converting chart to dict"""
        data = sample_single_chart.to_dict()
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "published_date" in data
        assert "entries" in data
        # Date should be ISO format string
        assert isinstance(data["published_date"], str)
        assert data["published_date"] == "2026-01-21"
