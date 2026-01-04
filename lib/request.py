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

def chat_completions(req, config):
    """request completions to OpenAI (compatible) API server"""
    endpoint = get_endpoint(config)
    return _post(endpoint, "/v1/chat/completions", req)

def get_endpoint(config={}) -> str:
    default_endpoint = "http://localhost:8080"
    return config.get("provider", {}).get("endpoint", default_endpoint)
