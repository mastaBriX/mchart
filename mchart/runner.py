"""Scrapy spider runner for synchronous execution

Provides utilities to run Scrapy spiders from synchronous code and collect
their results. Uses multiprocessing to avoid Twisted reactor restart issues.
"""

import multiprocessing
from typing import Any, Optional


def _run_spider_in_process(spider_cls, spider_kwargs, settings_override,
                           result_queue):
    """Target function for the subprocess. Runs the spider and collects items.

    Items are collected via Scrapy signals (bypassing pipelines) so that
    only simple dict-like data goes through the multiprocessing Queue.
    """
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from scrapy import signals as scrapy_signals

    settings = get_project_settings()
    settings.setmodule("mchart.settings", priority="project")

    # Disable pipelines for library usage - we assemble models in the provider
    settings.set("ITEM_PIPELINES", {}, priority="cmdline")

    if settings_override:
        for key, val in settings_override.items():
            settings.set(key, val, priority="cmdline")

    collected = []

    def _on_item_scraped(item, response, spider):
        # Convert Scrapy Item to plain dict for safe serialization
        collected.append(dict(item))

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(spider_cls)
    crawler.signals.connect(_on_item_scraped, signal=scrapy_signals.item_scraped)
    process.crawl(crawler, **spider_kwargs)
    process.start()

    result_queue.put(collected)


def run_spider(spider_cls, settings_override: Optional[dict[str, Any]] = None,
               **spider_kwargs) -> list[dict]:
    """Run a Scrapy spider synchronously and return collected items.

    Uses multiprocessing to avoid Twisted reactor restart issues when
    running multiple crawls in the same Python process.

    Args:
        spider_cls: The spider class to run.
        settings_override: Optional dict of Scrapy settings to override.
        **spider_kwargs: Keyword arguments passed to the spider constructor.

    Returns:
        List of raw item dicts yielded by the spider.
    """
    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue()

    proc = ctx.Process(
        target=_run_spider_in_process,
        args=(spider_cls, spider_kwargs, settings_override or {}, result_queue),
    )
    proc.start()
    proc.join()

    if not result_queue.empty():
        return result_queue.get()
    return []
