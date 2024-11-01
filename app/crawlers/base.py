from abc import ABC, abstractmethod
# from bs4 import BeautifulSoup
# import request


class Crawler(ABC):
    @abstractmethod
    def connect(self, **kwags):
        pass

    @abstractmethod
    def get_html(self, url):
        pass
