from bs4 import BeautifulSoup
from threading import Thread
import requests
import time
import argparse
import urllib
from urllib.parse import urlparse, urljoin


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        super().__init__()
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url):
        """
        Retorna o conteúdo da url (em binário) apenas se o conteúdo for HTML
        """
        headers = {
            "User-Agent": self.obj_scheduler.str_usr_agent,
        }
        url = obj_url.geturl()
        r = requests.get(url, headers=headers)

        return r.content if "text/html" in r.headers.get("content-type") else None

    def discover_links(self, obj_url, int_depth, bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")

        # Check if page can be indexed
        robots_no_index = soup.findAll(
            "meta", {"name": "robots", "content": "noindex"})
        agent_no_index = soup.findAll(
            "meta", {"name": self.obj_scheduler.str_usr_agent, "content": "noindex"})
        no_index = agent_no_index is None or robots_no_index is None

        # Check if page can be followed
        robots_no_folllow = soup.findAll(
            "meta", {"name": "robots", "content": "nofollow"})
        agent_no_follow = soup.findAll(
            "meta", {"name": self.obj_scheduler.str_usr_agent, "content": "nofollow"})
        no_follow = agent_no_follow is None or robots_no_folllow is None

        if not no_index:
            for link in soup.select("a[href]"):
                if (obj_url.geturl() in link["href"] or not "http" in link["href"]) and not no_follow:
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
        """
        Solicita ao escalonador uma nova url
        """
        url = self.obj_scheduler.get_next_url()
        if url[0] and self.obj_scheduler.can_fetch_page(url[0]):
            urbi = self.request_url(url[0])
            if urbi is not None:
                self.obj_scheduler.count_fetched_page()
                print(url[0].geturl())
                for url, depth in self.discover_links(url[0], url[1], urbi):
                    self.obj_scheduler.add_new_page(url, depth)

    def run(self):
        print("Thread started!")
        while not self.obj_scheduler.has_finished_crawl():
            self.crawl_new_url()
