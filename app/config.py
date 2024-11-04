from decouple import config as dcfg

PINECONE_TOKEN = dcfg("PINECONE_TOKEN")
POE_TOKEN = dcfg("POE_TOKEN")
HUADIAN_USER = dcfg("HUADIAN_USER")
HUADIAN_PASSWORD = dcfg("HUADIAN_PASSWORD")
OSS_BUCKET = dcfg('OSS_BUCKET')
OSS_ENDPOINT = dcfg('OSS_ENDPOINT', "https://oss-cn-hangzhou.aliyuncs.com")
OSS_KEY = dcfg('OSS_KEY')
OSS_SEC = dcfg('OSS_SEC')

assert PINECONE_TOKEN and POE_TOKEN and HUADIAN_PASSWORD and \
    HUADIAN_USER and OSS_KEY and OSS_SEC and OSS_BUCKET
