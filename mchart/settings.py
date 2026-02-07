"""Scrapy settings for mchart project"""

BOT_NAME = "mchart"

SPIDER_MODULES = ["mchart.spiders"]
NEWSPIDER_MODULE = "mchart.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 1

# Download delay between requests to the same domain
DOWNLOAD_DELAY = 0

# Default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "mchart.middlewares.RetryWithBackoffMiddleware": 550,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "mchart.pipelines.ChartAssemblyPipeline": 300,
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# Download timeout
DOWNLOAD_TIMEOUT = 30

# Disable logging by default (library usage)
LOG_ENABLED = False

# Request fingerprinter implementation
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Twisted reactor (use asyncio reactor)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEED_EXPORT_ENCODING = "utf-8"
