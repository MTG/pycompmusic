import logging
import six
from six.moves.urllib import parse as urllibparse

import requests
import requests.adapters

logger = logging.getLogger("dunya")

HOSTNAME = "dunya.compmusic.upf.edu"
TOKEN = None
session = requests.Session()
session.mount('http://' + HOSTNAME, requests.adapters.HTTPAdapter(max_retries=5))


class HTTPError(Exception):
    pass


class ConnectionError(Exception):
    pass


def set_hostname(hostname):
    """ Change the hostname of the dunya API endpoint.

    Arguments:
        hostname: The new dunya hostname to set

    """
    global HOSTNAME
    HOSTNAME = hostname


def set_token(token):
    """ Set an access token. You must call this before you can make
    any other calls.

    Arguments:
        token: your access token

    """
    global TOKEN
    TOKEN = token


def _get_paged_json(path, **kwargs):
    extra_headers = None
    if 'extra_headers' in kwargs:
        extra_headers = kwargs.get('extra_headers')
        del kwargs['extra_headers']
    nxt = _make_url(path, **kwargs)
    logger.debug("initial paged to %s", nxt)
    ret = []
    while nxt:
        res = _dunya_url_query(nxt, extra_headers=extra_headers)
        res = res.json()
        ret.extend(res.get("results", []))
        nxt = res.get("next")
    return ret


def _dunya_url_query(url, extra_headers=None):
    logger.debug("query to '%s'" % url)
    if not TOKEN:
        raise ConnectionError("You need to authenticate with `set_token`")

    headers = {"Authorization": "Token %s" % TOKEN}
    if extra_headers:
        headers.update(extra_headers)

    g = session.get(url, headers=headers)
    try:
        g.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPError(e)
    return g


def _dunya_post(url, data=None, files=None):
    data = data or {}
    files = files or {}
    logger.debug("post to '%s'" % url)
    if not TOKEN:
        raise ConnectionError("You need to authenticate with `set_token`")
    headers = {"Authorization": "Token %s" % TOKEN}
    p = requests.post(url, headers=headers, data=data, files=files)
    try:
        p.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPError(e)
    return p


def _make_url(path, **kwargs):
    if not kwargs:
        kwargs = {}
    for key, value in kwargs.items():
        kwargs[key] = six.text_type(value)
    url = urllibparse.urlunparse((
        'http',
        HOSTNAME,
        '%s' % path,
        '',
        urllibparse.urlencode(kwargs),
        ''
    ))
    return url


def _dunya_query_json(path, **kwargs):
    """Make a query to dunya and expect the results to be JSON"""
    g = _dunya_url_query(_make_url(path, **kwargs))
    return g.json() if g else None


def _dunya_query_file(path, **kwargs):
    """Make a query to dunya and return the raw result"""
    g = _dunya_url_query(_make_url(path, **kwargs))
    if g:
        cl = g.headers.get('content-length')
        content = g.content
        if cl and int(cl) != len(content):
            logger.warning("Indicated content length is not the same as returned content. Some data may be missing")
        return content
    else:
        return None
