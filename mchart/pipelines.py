"""Scrapy pipelines for mchart

Processes raw scraped items into structured Pydantic models.
"""

from .items import ChartPageItem
from .models import Chart, ChartEntry, ChartMetadata, Song, Album


class ChartAssemblyPipeline:
    """Assembles ChartPageItem into a Chart Pydantic model"""

    def process_item(self, item, spider):
        if not isinstance(item, ChartPageItem):
            return item

        chart_type = item.get("chart_type", "single")
        entries = []

        for raw_entry in item.get("entries", []):
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
            provider=item.get("provider", ""),
            title=item.get("chart_title", ""),
            description=item.get("description", ""),
            url=item.get("url", ""),
            type=chart_type,
        )

        chart = Chart(
            metadata=metadata,
            published_date=item["published_date"],
            entries=entries,
            chart_type=chart_type,
        )

        return chart
