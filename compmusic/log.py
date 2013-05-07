import logging

log = logging.getLogger('pycompmusic')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)
