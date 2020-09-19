from bs4 import BeautifulSoup
from threading import Thread
import requests
import urllib
from urllib.parse import urlparse, urljoin


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url):
        headers = {
            'User-Agent': 'botzuck',
        }
        url = obj_url.geturl()
        if not '.html' in obj_url.path and '.' in obj_url.path:
            return None
        else:
            return requests.get(url, headers=headers).content

    def discover_links(self, obj_url, int_depth, bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        for link in soup.select(None):
            obj_new_url = None
            int_new_depth = None

            yield obj_new_url, int_new_depth

    def crawl_new_url(self):
        """
            Coleta uma nova URL, obtendo-a do escalonador
        """
        pass

    def run(self):
        """
            Executa coleta enquanto houver páginas a serem coletadas
        """
        pass
