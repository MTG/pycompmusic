eyed3api = None
try:
    import eyed3
    eyed3api = "new"
except ImportError:
    pass

try:
    import eyeD3
    eyed3api = "old"
except ImportError:
    pass

if not eyed3api:
    raise ImportError("Cannot find eyed3 or eyeD3")

def has_musicbrainz_tags(fname):
    """Return true if a file has musicbrainz tags set."""
    pass

def has_coverart(fname):
    """Return true if a file has embedded coverart."""
    pass

def _mb_id(tag, key):
    if eyed3api == "old":
        tags = [t for t in tag.getUserTextFrames() if t.description == key]
        if len(tags):
            return tags[0].text
        else:
            return None
    elif eyed3api == "new":
        pass

def mb_release_id(tag):
    """Return the Musicbrainz release ID in an eyed3 tag"""
    return _mb_id(tag, "MusicBrainz Album Id")

def mb_artist_id(tag):
    return _mb_id(tag, "MusicBrainz Artist Id")

def mb_recording_id(tag):
    ids = tag.getUniqueFileIDs()
    if len(ids):
        i = ids[0]
        if i.owner_id == "http://musicbrainz.org":
            return i.id
    return None

def file_metadata(fname):
    if eyed3api == "old":
        audfile = eyeD3.Mp3AudioFile(fname)
        duration = audfile.play_time
        artist = audfile.tag.getArtist()
        title = audfile.tag.getTitle()
        album = audfile.tag.getAlbum()
    elif eyed3api == "new":
        audfile = eyed3.load(fname)
        duration = audfile.info.time_secs
        artist = audfile.tag.artist
        title = audfile.tag.title
        album = audfile.tag.album
    return {"file": fname,
            "duration": duration,
            "meta": {"artist": artist,
                     "title": title,
                     "album": album
                    }
           }
