import requests
import compmusic
import os

AUDIO_FILES = "/home/alastair/audio/carnatic"
RELEASE_MAP = {}

def get_coverart_from_directories(directories=[]):
    """Get the cover art inside a file, otherwise try on CAA"""
    for d in directories:
        files = os.listdir(d)
        files = [f for f in files if compmusic.is_mp3_file(f)]
        for f in files:
            coverart = compmusic.get_coverart(os.path.join(d, f))
            if coverart:
                return coverart
    return None

def get_coverart_from_caa(releaseid):
    """Get the cover art inside a file, otherwise try on CAA"""
    url = "http://coverartarchive.org/release/%s/front" % releaseid
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    return None
