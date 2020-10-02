from crawler.scheduler import Scheduler
from crawler.page_fetcher import PageFetcher
from urllib.parse import urlparse
import ssl

if __name__ == "__main__":
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    url_seeds = ["http://www.uol.com.br/"]
    scheduler = Scheduler(
        str_usr_agent="xxbot",
        int_page_limit=30,
        int_depth_limit=3,
        arr_urls_seeds=url_seeds,
    )

    page_fetchers = [PageFetcher(scheduler) for _ in range(0, 5)]
    page_fetchers[0].start()
