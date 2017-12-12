import logging
logger = logging.getLogger("dunya")
logger.setLevel(logging.INFO)

from compmusic.dunya.conn import set_hostname, set_token, HTTPError
from compmusic.dunya.docserver import *
from compmusic.dunya import carnatic
from compmusic.dunya import hindustani
from compmusic.dunya import makam
