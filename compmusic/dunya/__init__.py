import logging
logger = logging.getLogger("dunya")
logger.setLevel(logging.INFO)

from conn import set_hostname, set_token
from docserver import *
import carnatic
