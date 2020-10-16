from crawler.scheduler import Scheduler
from crawler.page_fetcher import PageFetcher
from urllib.parse import urlparse
import ssl

def execute_zuck(url_seeds,int_page_limit,int_depth_limit,numthread):

    scheduler = Scheduler(str_usr_agent="zuckinhObot",
                                int_page_limit=int_page_limit,
                                int_depth_limit=int_depth_limit,
                                arr_urls_seeds=url_seeds)

    page_fetchers = [PageFetcher(scheduler) for _ in range(0, numthread)]

    for pg_fetcher in page_fetchers:
        pg_fetcher.start()
    return scheduler
