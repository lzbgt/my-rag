from decouple import config as dcfg

PINECONE_TOKEN = dcfg("PINECONE_TOKEN")
POE_TOKEN = dcfg("POE_TOKEN")
HUADIAN_USER = dcfg("HUADIAN_USER")
HUADIAN_PASSWORD = dcfg("HUADIAN_PASSWORD")

assert PINECONE_TOKEN and POE_TOKEN and HUADIAN_PASSWORD and HUADIAN_USER
