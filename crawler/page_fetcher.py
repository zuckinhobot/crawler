from bs4 import BeautifulSoup
from threading import Thread
import requests
import argparse
import urllib
from urllib.parse import urlparse, urljoin


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url):
        headers = {
            "User-Agent": "botzuck",
        }
        url = obj_url.geturl()
        r = requests.get(url, headers=headers)

        return r.content if "text/html" in r.headers.get("content-type") else None

    def discover_links(self, obj_url, int_depth, bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        for link in soup.select("a[href]"):
            if obj_url.geturl() in link["href"] or not "http" in link["href"]:
                url = (
                    urlparse(link["href"])
                    if "http" in link["href"]
                    else urlparse(obj_url.geturl() + "/" + link["href"])
                )
                obj_new_url = url
                int_new_depth = int_depth + 1
            else:
                obj_new_url = urlparse(link["href"])
                int_new_depth = 0

            yield obj_new_url, int_new_depth

    def crawl_new_url(self):
        url = self.obj_scheduler.get_next_url()
        if self.obj_scheduler.can_fetch_page(url):
            urbi = self.request_url(url)
            if urbi is not None:
                print(url[0].geturl())
                for url, depth in self.discover_links(url[0], url[1], urbi):
                    self.obj_scheduler.add_new_page(url, depth)
        pass

    def run(self):
        while not self.obj_scheduler.has_finished_crawl():
            self.crawl_new_url()
        pass
