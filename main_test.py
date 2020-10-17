from crawler.scheduler import Scheduler
from crawler.page_fetcher import PageFetcher
from urllib.parse import urlparse
import ssl

def execute_zuck(url_seeds,int_page_limit,int_depth_limit,numthread):

    for threads in numthread:

        scheduler = Scheduler(str_usr_agent="zuckinhObot",
                                    int_page_limit=int_page_limit,
                                    int_depth_limit=int_depth_limit,
                                    arr_urls_seeds=url_seeds,
                                    numthread=threads,
                                    v_numthreads=numthread
                              )

        page_fetchers = [PageFetcher(scheduler) for _ in range(0, threads)]

        for pg_fetcher in page_fetchers:
            pg_fetcher.start()