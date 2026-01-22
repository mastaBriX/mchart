"""Pytest configuration and fixtures"""

import pytest
from datetime import date
from mchart.models import Song, Album, ChartEntry, ChartMetadata, Chart


@pytest.fixture
def sample_song():
    """Sample song for testing"""
    return Song(
        title="Test Song",
        artist="Test Artist",
        artists=["Test Artist"],
        image="https://example.com/image.jpg",
        album="Test Album"
    )


@pytest.fixture
def sample_album():
    """Sample album for testing"""
    return Album(
        title="Test Album",
        artist="Test Artist",
        artists=["Test Artist"],
        image="https://example.com/image.jpg"
    )


@pytest.fixture
def sample_single_entry(sample_song):
    """Sample chart entry for single chart"""
    return ChartEntry(
        song=sample_song,
        rank=1,
        weeks_on_chart=5,
        last_week=2,
        peak_position=1
    )


@pytest.fixture
def sample_album_entry(sample_album):
    """Sample chart entry for album chart"""
    return ChartEntry(
        album=sample_album,
        rank=1,
        weeks_on_chart=3,
        last_week=0,
        peak_position=1
    )


@pytest.fixture
def sample_single_metadata():
    """Sample metadata for single chart"""
    return ChartMetadata(
        provider="billboard",
        title="Billboard Hot 100",
        description="Test description",
        url="https://www.billboard.com/charts/hot-100",
        type="single"
    )


@pytest.fixture
def sample_album_metadata():
    """Sample metadata for album chart"""
    return ChartMetadata(
        provider="billboard",
        title="Billboard 200",
        description="Test description",
        url="https://www.billboard.com/charts/billboard-200",
        type="album"
    )


@pytest.fixture
def sample_single_chart(sample_single_metadata, sample_single_entry):
    """Sample single chart"""
    return Chart(
        metadata=sample_single_metadata,
        published_date=date(2026, 1, 21),
        entries=[sample_single_entry]
    )


@pytest.fixture
def sample_album_chart(sample_album_metadata, sample_album_entry):
    """Sample album chart"""
    return Chart(
        metadata=sample_album_metadata,
        published_date=date(2026, 1, 21),
        entries=[sample_album_entry]
    )
