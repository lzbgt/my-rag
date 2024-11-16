from io import BytesIO
from hashlib import md5
import asyncio
import fastapi_poe as fp
import mimetypes
from io import BytesIO

from app.utils.mylogger import get_logger
logger = get_logger(__name__)

# Create an asynchronous function to encapsulate the async for loop


class Poe():
    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.buff = BytesIO()

    async def async_get_responses(self, messages):
        async for partial in fp.get_bot_response(messages=messages, bot_name="ChatGPT-4o-Latest-128k", api_key=self.api_key):
            # print(partial.text, end='', flush=True)
            self.buff.write(partial.text.encode())

    def get_response(self, q: str, attachs: list = []):
        atts = []
        for a in attachs:
            mtype = mimetypes.guess_type(a)[0]
            name = a.split('/')[-1]
            atts.append(fp.Attachment(
                url=attachs[0], content_type=mtype, name=name))

        message = fp.ProtocolMessage(
            role="user", content=q, attachments=atts)

        asyncio.run(self.async_get_responses([message]))
        self.buff.seek(0)
        return self.buff.read().decode()


if __name__ == "__main__":
    from app.crawlers.huadian import HuadianCrawler
    from bs4 import BeautifulSoup
    from app.utils.oss import oss_upload_buff
    from app.config import HUADIAN_PASSWORD, HUADIAN_USER, POE_TOKEN
    import sys

    cr = HuadianCrawler()
    cr.connect(username=HUADIAN_USER, password=HUADIAN_PASSWORD)
    try:
        text = cr.get_html(
            f"http://school.huadianline.com/index.php?app=exams&mod=Index&act=examsroom&paper_id={sys.argv[1]}&joinType=1")
    except Exception as e:
        logger.exception(e)
        exit()
    bs = BeautifulSoup(text, "html.parser")
    r = bs.select_one("ul.test-paper-box")
    if not r:
        logger.error("未找到试卷")
        exit()
    logger.info(r.prettify())
    buff = r.encode()
    hash = md5(buff).hexdigest()
    # logger.info(hash)
    # oss_upload_buff(buff, f"huadian/exam/{hash}.html")
    # 1c865dc004f83ce90bfdc9989d24ec85.html
    llm = Poe(POE_TOKEN)
    r = llm.get_response(
        f"你是一个研究生. 作答下面试卷中的全部试题. 对于选择题, 给出正确答案的编号并给出你的解析, 不用重复题目的内容. 对于其他类型的试题, 给出试题本身的精炼描述和你回答该题目的答案及解析.\n\n{r.prettify()}")
    print(r)
    with open(f"{sys.argv[1]}.md", "w") as f:
        f.write(r)
