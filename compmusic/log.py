import logging

log = logging.getLogger('pycompmusic')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

eyelog = logging.getLogger('eyed3')
eyech = logging.StreamHandler()
eyech.setLevel(logging.ERROR)
eyelog.addHandler(eyech)


