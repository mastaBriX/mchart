"""Scrapy middlewares for mchart"""

import time
import logging

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

logger = logging.getLogger(__name__)


class RetryWithBackoffMiddleware(RetryMiddleware):
    """Retry middleware with exponential backoff for rate-limited requests"""

    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # Calculate backoff delay
            retry_count = request.meta.get("retry_times", 0)
            delay = min(2 ** retry_count, 16)
            logger.debug(
                f"Retrying {request.url} (status {response.status}) "
                f"after {delay}s backoff"
            )
            time.sleep(delay)
            return self._retry(request, reason, spider) or response
        return response


class MChartSpiderMiddleware:
    """Spider middleware for mchart spiders"""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def spider_opened(self, spider):
        logger.debug(f"Spider opened: {spider.name}")
