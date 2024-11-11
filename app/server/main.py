import sys
from app.config import HUADIAN_PASSWORD, HUADIAN_USER, POE_TOKEN
from app.utils.oss import oss_upload_buff
from bs4 import BeautifulSoup
from app.crawlers.huadian import HuadianCrawler
from app.rag.llm import Poe
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import Response
import uvicorn
from app.utils.mylogger import get_logger
from hashlib import md5
import gzip
import json
import os

logger = get_logger(__name__)
app = FastAPI()


def verify_secret(sec: str):
    if sec != "Hz20012056":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret key",
        )


@app.post("/api/qa")
def llm_qa(school: int, paper_id: int, sec: str = Depends(verify_secret,)):
    logger.info(f"school: {school}, paper_id: {paper_id}")

    if os.path.exists(f"{paper_id}.html") and os.path.exists(f"{paper_id}.md"):
        a = open(f"{paper_id}.md").read()
        r = open(f"{paper_id}.html").read()
        hash = md5(r.encode()).hexdigest()
    else:
        cr = HuadianCrawler()
        cr.connect(username=HUADIAN_USER, password=HUADIAN_PASSWORD)
        try:
            text = cr.get_html(
                f"http://school.huadianline.com/index.php?app=exams&mod=Index&act=examsroom&paper_id={paper_id}&joinType=1")
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部问题",
            )
        bs = BeautifulSoup(text, "html.parser")
        r = bs.select_one("ul.test-paper-box")
        if not r:
            logger.error(f"未找到试卷: {paper_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到试卷",
            )
        logger.info(r.prettify())
        r = r.prettify()
        with open(f"{paper_id}.html", "w") as f:
            f.write(r)
        buff = r.encode()
        hash = md5(buff).hexdigest()
        # logger.info(hash)
        # oss_upload_buff(buff, f"huadian/exam/{hash}.html")
        # 1c865dc004f83ce90bfdc9989d24ec85.html
        llm = Poe(POE_TOKEN)
        a = llm.get_response(
            f"请作答下面试卷中的所有题. 对于选择题, 只给出编号即可. 所有题目都给出精炼的解析:\n\n{r}")
        with open(f"{paper_id}.md", "w") as f:
            f.write(a)

    data = {
        "school": school,
        "paper_id": paper_id,
        "answer": a,
        "hash": hash,
        "paper": r
    }
    cdata = gzip.compress(json.dumps(data).encode("utf-8"))
    headers = {
        'Content-Encoding': 'gzip',
        'Content-Type': 'application/json'
    }
    return Response(cdata, headers=headers)


if __name__ == "__main__":
    uvicorn.run("app.server.main:app", host="0.0.0.0", port=8000, workers=2)
