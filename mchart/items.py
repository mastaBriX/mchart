"""Scrapy item definitions

Maps scraped data to structured items that are converted to Pydantic models
via pipelines.
"""

import scrapy


class ChartEntryItem(scrapy.Item):
    """Raw chart entry scraped from a page"""

    rank = scrapy.Field()
    title = scrapy.Field()
    artist = scrapy.Field()
    artists = scrapy.Field()
    image = scrapy.Field()
    weeks_on_chart = scrapy.Field()
    last_week = scrapy.Field()
    peak_position = scrapy.Field()
    # Indicates whether this is an album entry or song entry
    entry_type = scrapy.Field()


class ChartPageItem(scrapy.Item):
    """Metadata about the chart page itself"""

    provider = scrapy.Field()
    chart_name = scrapy.Field()
    chart_title = scrapy.Field()
    chart_type = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    published_date = scrapy.Field()
    entries = scrapy.Field()
