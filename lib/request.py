import logging
import json
import urllib.request
import urllib.parse

# for debug
from pathlib import Path

logger = logging.getLogger(__name__)

def _post(endpoint, path, body):
    url = urllib.parse.urljoin(endpoint, path)
    #data = json.dumps(body)
    data = body.encode("utf8")
    req = urllib.request.Request(url, data, method="POST")
    req.add_header("content-type", "application/json")
    logger.info(f"""POST {url} (body: {len(data)}B)""")
    
    resp = urllib.request.urlopen(req)
    result_json = json.load(resp)
    #result = resp.read()
    logger.debug(f"""result: {result_json}""")
    return result_json

def chat_completions(req):
    return _post("http://localhost:8080", "/v1/chat/completions", req)

## for test
def _chat_completions(req):
    p = Path(__file__)
    fname = p.parent.parent / "tmp.json"
    with fname.open("r", encoding="utf8") as fp:
        rs = json.load(fp)
    return rs
