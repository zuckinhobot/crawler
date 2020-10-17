# -*- coding: utf-8 -*-

from urllib import robotparser
from util.threads import synchronized
from collections import OrderedDict
from urllib.parse import urlparse
from .domain import Domain
import time


class Scheduler:
    # tempo (em segundos) entre as requisições
    TIME_LIMIT_BETWEEN_REQUESTS = 30
    Time_fim = 0
    Time_init = time.time()

    def __init__(self, str_usr_agent, int_page_limit, int_depth_limit, arr_urls_seeds, numthreads):

        """
            Inicializa o escalonador. Atributos:
                - `str_usr_agent`: Nome do `User agent`. Usualmente, é o nome do navegador, em nosso caso,  será o nome do coletor (usualmente, terminado em `bot`)
                - `int_page_limit`: Número de páginas a serem coletadas
                - `int_depth_limit`: Profundidade máxima a ser coletada
                - `int_page_count`: Quantidade de página já coletada
                - `dic_url_per_domain`: Fila de URLs por domínio (explicado anteriormente)
                - `set_discovered_urls`: Conjunto de URLs descobertas, ou seja, que foi extraída em algum HTML e já adicionadas na fila - mesmo se já ela foi retirada da fila. A URL armazenada deve ser uma string.
                - `dic_robots_per_domain`: Dicionário armazenando, para cada domínio, o objeto representando as regras obtidas no `robots.txt`
        """
        self.str_usr_agent = str_usr_agent
        self.int_page_limit = int_page_limit
        self.int_depth_limit = int_depth_limit
        self.int_page_count = 0

        self.numthreads = numthreads

        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}

        for url_seed in arr_urls_seeds:
            self.add_new_page(urlparse(url_seed), 0)

    @synchronized
    def count_fetched_page(self):
        """
            Contabiliza o número de paginas já coletadas
        """
        self.int_page_count += 1

    def has_finished_crawl(self):
        """
            Verifica se finalizou a coleta
        """
        if self.int_page_count > self.int_page_limit:
            self.Time_fim = time.time()
            self.registerData()

            print("Thread ended!")
            return True
        return False

    @synchronized
    def can_add_page(self, obj_url, int_depth):
        """
            Retorna verdadeiro caso  profundade for menor que a maxima
            e a url não foi descoberta ainda
        """
        return (
            int_depth <= self.int_depth_limit
            and obj_url.geturl() not in self.set_discovered_urls
        )

    @synchronized
    def add_new_page(self, obj_url, int_depth):
        """
            Adiciona uma nova página
            obj_url: Objeto da classe ParseResult com a URL a ser adicionada
            int_depth: Profundidade na qual foi coletada essa URL
        """
        # https://docs.python.org/3/library/urllib.parse.html
        if not self.can_add_page(obj_url, int_depth):
            return False

        domain_tuple = (obj_url, int_depth)
        if obj_url.netloc in self.dic_url_per_domain:
            self.dic_url_per_domain[obj_url.netloc].append(domain_tuple)
        else:
            new_domain = Domain(obj_url.netloc, self.TIME_LIMIT_BETWEEN_REQUESTS)
            self.dic_url_per_domain[new_domain] = [domain_tuple]
        self.set_discovered_urls.add(obj_url.geturl())

        return True

    @synchronized
    def get_next_url(self):
        """
        Obtem uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """
        while True:
            try:
                dic_url_per_domain_copy = self.dic_url_per_domain.copy()
                any_domain_is_accessible = any(
                    domain.is_accessible() is True for domain in self.dic_url_per_domain
                )
                has_any_urls_left = len(self.dic_url_per_domain.values()) > 0

                if any_domain_is_accessible or not has_any_urls_left:
                    break
            except:
                pass

        for domain in dic_url_per_domain_copy:
            if len(self.dic_url_per_domain[domain]) > 0:
                if domain.is_accessible():
                    domain.accessed_now()
                    return self.dic_url_per_domain[domain].pop(0)

            else:
                self.dic_url_per_domain.pop(domain, None)

        return None, None

    @synchronized
    def can_fetch_page(self, obj_url):
        """
        Verifica, por meio do robots.txt se uma determinada URL pode ser coletada
        """
        if not obj_url.netloc in self.dic_robots_per_domain:
            try:
                rp = robotparser.RobotFileParser()
                rp.set_url("http://" + obj_url.netloc + "/robots.txt")
                rp.read()

                int_crawl_delay = rp.crawl_delay(self.str_usr_agent)

                if int_crawl_delay is not None and int_crawl_delay > self.TIME_LIMIT_BETWEEN_REQUESTS:
                    self.dic_url_per_domain[obj_url.netloc].int_time_limit_seconds = int_crawl_delay
                
                self.dic_robots_per_domain[obj_url.netloc] = rp
            except Exception:
                print(f"Failed checking robots.txt from {obj_url.netloc}")

        if obj_url.netloc not in self.dic_robots_per_domain:
            return True

        robot = self.dic_robots_per_domain[obj_url.netloc]
        return robot.can_fetch(self.str_usr_agent, obj_url.geturl())

    @synchronized
    def registerData(self):

        f = open("data.txt", "a")
        f.write(str(self.numthreads) + "," + str(self.Time_fim - self.Time_init) + "\n")
