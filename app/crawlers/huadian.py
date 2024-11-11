from .base import *
import requests
from app.utils.mylogger import get_logger
from app.config import *

logger = get_logger(__name__)


class HuadianCrawler(Crawler):
    def __init__(self) -> None:
        super().__init__()

    def connect(self, **kwargs):
        self.url = 'http://school.huadianline.com/index.php?app=basic&mod=Passport&act=ajaxLogin'
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        logger.info(f"connecting to {self.url} with username {self.username}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            # Explicitly specify keep-alive (usually not necessary)
            'Connection': 'keep-alive',
            "Referer": f"http://school.huadianline.com"
        })

        res = self.session.post(
            self.url, data={'log_username': self.username, 'log_pwd': self.password})

        if res.status_code != 200:
            errmsg = f"{res.status_code}: {res.text}"
            logger.error(errmsg)
            raise Exception(errmsg)

    def get_html(self, url, **kwargs):
        res = self.session.get(url, timeout=60)
        if res.status_code != 200:
            errmsg = f"{res.status_code}: {res.text}"
            logger.error(errmsg)
            raise Exception(errmsg)
        return res.text

    def close(self):
        self.session.close()


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    crawler = HuadianCrawler()
    crawler.connect(username=HUADIAN_USER, password=HUADIAN_PASSWORD)
    text = crawler.get_html(
        "http://school.huadianline.com/index.php?app=exams&mod=Index&act=examsroom&paper_id=640&joinType=1")
    bs = BeautifulSoup(text, "html.parser")
    r = bs.select_one("ul.test-paper-box")
    logger.info(r.prettify())
