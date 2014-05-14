
import os
import requests
import logging
logger = logging.getLogger("dunya")

import conn
import docserver

def get_recordings():
    """ Get a list of hindustani recordings in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing recording information.
    {"mbid": Musicbrainz recording id,
     "title": Title of the recording
    }
    For additional information about each recording use the
    `get_recording` method. """
    return conn._get_paged_json("api/hindustani/recording")

def get_recording(rmbid):
    """ Get specific information about a recording. 
    Arguments:
      rmbid: A recording mbid
    Returns: mbid, title, artists, raags, taals, layas, forms and works
             artists include performance relationships attached
             to the recording, the release, and the release artists.
    """
    return conn._dunya_query_json("api/hindustani/recording/%s" % rmbid)

def get_artists():
    """ Get a list of Hindustani artists in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing artist information.
    {"mbid": Musicbrainz artist id,
     "name": Name of the artist
    }
    For additional information about each artist use the
    `get_artist` method. """
    return conn._get_paged_json("api/hindustani/artist")

def get_artist(ambid):
    """ Get specific information about an artist.
    Arguments:
      ambid: An artist mbid
    Returns: mbid, name, releases, instruments, recordings
             releases, instruments and recordings include information
             from recording- and release-level relationships, as
             well as release artists
    """
    return conn._dunya_query_json("api/hindustani/artist/%s" % ambid)

def get_releases():
    """ Get a list of Hindustani releases in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing release information.
    {"mbid": Musicbrainz release id,
     "title": title of the release
    }
    For additional information about each release use the
    `get_release` method. """
    return conn._get_paged_json("api/hindustani/release")

def get_release(cmbid):
    """ Get specific information about a release. 
    Arguments:
      cmbid: A release mbid
    Returns: mbid, title, artists, tracks, release artists
             artists includes performance relationships attached
             to the recordings, the release, and the release artists.
    """
    return conn._dunya_query_json("api/hindustani/release/%s" % cmbid)

def get_works():
    """ Get a list of Hindustani works in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing work information.
    {"mbid": Musicbrainz work id,
     "name": work name
    }
    For additional information about each work use the
    `get_work` method. """
    return conn._get_paged_json("api/hindustani/work")

def get_work(wmbid):
    """ Get specific information about a work.
    Arguments:
      wmbid: A work mbid
    Returns: mbid, title, recordings
    """
    return conn._dunya_query_json("api/hindustani/work/%s" % wmbid)

def get_raags():
    """ Get a list of Hindustani raags in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing raag information.
    {"id": raag id,
     "name": name of the raag
    }
    For additional information about each raag use the
    `get_raag` method. """
    return conn._get_paged_json("api/hindustani/raag")

def get_raag(rid):
    """ Get specific information about a raag.
    Arguments:
      rid: A raag id
    Returns: id, name, artists, recordings, composers 
             artists includes artists with recording-level 
             relationships to a recording with this raag
    """
    return conn._dunya_query_json("api/hindustani/raag/%s" % str(rid))

def get_taals():
    """ Get a list of Hindustani taals in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing taal information.
    {"id": taal id,
     "name": name of the taal
    }
    For additional information about each taal use the
    `get_taal` method. """
    return conn._get_paged_json("api/hindustani/taal")

def get_taal(tid):
    """ Get specific information about a taal.
    Arguments:
      tid: A taal id
    Returns: id, name, recordings, composers
    """
    return conn._dunya_query_json("api/hindustani/taal/%s" % str(tid))
    
def get_layas():
    """ Get a list of Hindustani layas in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing laya information.
    {"id": laya id,
     "name": name of the laya 
    }
    For additional information about each laya use the
    `get_laya` method. """
    return conn._get_paged_json("api/hindustani/laya")

def get_laya(lid):
    """ Get specific information about a laya.
    Arguments:
      lid: A laya id
    Returns: id, name, recordings
    """
    return conn._dunya_query_json("api/hindustani/laya/%s" % str(lid))

def get_forms():
    """ Get a list of Hindustani forms in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing form information.
    {"id": form  id,
     "name": name of the form 
    }
    For additional information about each form use the
    `get_form` method. """
    return conn._get_paged_json("api/hindustani/form")

def get_form(fid):
    """ Get specific information about a form.
    Arguments:
      fid: A form id
    Returns: id, name, artists, recordings
             artists includes artists with recording- and release-
             level relationships to a recording with this form
    """
    return conn._dunya_query_json("api/hindustani/form/%s" % str(fid))

def get_instruments():
    """ Get a list of Hindustani instruments in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing instrument information.
    {"id": instrument id,
     "name": Name of the instrument
    }
    For additional information about each instrument use the
    `get_instrument` method. """
    return conn._get_paged_json("api/hindustani/instrument")

def get_instrument(iid):
    """ Get specific information about an instrument.
    Arguments:
      iid: An instrument id
    Returns: id, name, artists
             artists includes artists with recording- and release-
             level performance relationships of this instrument.
    """
    return conn._dunya_query_json("api/hindustani/instrument/%s" % str(iid))

def download_mp3(recordingid, location):
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    recording = get_recording(recordingid)
    release = get_release(recording["release"]["mbid"])
    title = recording["title"]
    artists = " and ".join([a["name"] for a in release["release_artists"]])
    contents = docserver.get_mp3(recordingid)
    name = "%s - %s.mp3" % (artists, title)
    path = os.path.join(location, name)
    open(path, "wb").write(contents)

def download_release(release_id, location):
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    release = get_release(release_id)
    artists = " and ".join([a["name"] for a in release["release_artists"]])
    releasename = release["title"]
    releasedir = os.path.join(location, "%s - %s" % (artists, releasename))
    for r in release["tracks"]:
        rid = r["mbid"]
        title = r["title"]
        contents = docserver.get_mp3(rid)
        name = "%s - %s.mp3" % (artists, title)
        path = os.path.join(releasedir, name)
        open(path, "wb").write(contents)
