import urlparse
import urllib
import requests

import logging
logger = logging.getLogger("dunya")

HOSTNAME = "dunya.compmusic.upf.edu"

def set_hostname(hostname):
    global HOSTNAME
    HOSTNAME = hostname

def _get_paged_json(path, **kwargs):
    ret = []
    res = _dunya_query_json(path, **kwargs)
    ret.extend(res.get("results", []))
    nxt = res.get("next")
    while nxt:
        res = _json_url_query(nxt)
        nxt = res.get("next")
        ret.extend(res.get("results", []))
    return ret

def _json_url_query(url):
    logger.debug("query to '%s'"%url)
    g = requests.get(url)
    g.raise_for_status()
    return g.json()

def _dunya_query(path, **kwargs):
    if not kwargs:
        kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, unicode):
            kwargs[key] = value.encode('utf8')
    url = urlparse.urlunparse((
        'http',
        HOSTNAME,
        '%s' % path,
        '',
        urllib.urlencode(kwargs),
        ''
    ))
    logger.debug("query to '%s'"%url)
    g = requests.get(url)
    g.raise_for_status()
    return g

def _dunya_query_json(path, **kwargs):
    """Make a query to dunya and expect the results to be JSON"""
    g = _dunya_query(path, **kwargs)
    return g.json()

def _dunya_query_file(path, **kwargs):
    """Make a query to dunya and return the raw result"""
    g = _dunya_query(path, **kwargs)
    return g.content
