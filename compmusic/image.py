import requests
import compmusic
import os

AUDIO_FILES = "/home/alastair/audio/carnatic"
RELEASE_MAP = {}

def load_album_data():
    """ create a map from releaseid->any audio file in that release """
    for root, dirs, files in os.walk(AUDIO_FILES):
        for f in files:
            fn = os.path.join(root, f)
            if compmusic.is_mp3_file(fn):
                print fn
                meta = compmusic.file_metadata(fn)
                print "meta", meta
                releaseid = meta["meta"]["releaseid"]
                if releaseid not in RELEASE_MAP:
                    RELEASE_MAP[releaseid] = fn

def get_coverart_for_release(releaseid):
    """Get the cover art inside a file, otherwise try on CAA"""
    if not RELEASE_MAP:
        load_album_data()
    if releaseid in RELEASE_MAP:
        img = compmusic.get_coverart(RELEASE_MAP[releaseid])
    else:
        url = "http://coverartarchive.org/release/%s/front" % releaseid
        r = requests.get(url)
        if r.status_code == 200:
            img = r.content
        else:
            img = None
    return img
