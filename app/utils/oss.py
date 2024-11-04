"""
Author: Bruce Lu
Email: lzbgt_AT_icloud.com
"""

import requests
import oss2
from app.config import OSS_KEY, OSS_BUCKET, OSS_ENDPOINT, OSS_SEC
from app.utils.mylogger import get_logger
logger = get_logger(__name__)

auth = oss2.ProviderAuth(
    oss2.credentials.StaticCredentialsProvider(OSS_KEY, OSS_SEC))
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)


def oss_upload_file(filename: str, key: str):
    try:
        bucket.put_object_from_file(key, filename)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def oss_upload_buff(buff, key: str):
    try:
        bucket.put_object(key, buff)
        return True
    except Exception as e:
        logger.exception(e)
        return False


def oss_download(src_path: str, target: str):
    try:
        logger.info(f"oss download from src: {src_path} to target: {target}")
        bucket.get_object_to_file(src_path, target)
        return True
    except Exception as e:
        logger.exception(f"failed to download {src_path}: {str(e)}")
        return False
