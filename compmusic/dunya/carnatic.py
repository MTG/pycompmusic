import os
import requests
import logging
logger = logging.getLogger("dunya")

import conn
import docserver

def get_recordings():
    """ Get a list of carnatic recordings in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing recording information.
    {"mbid": Musicbrainz recording id,
     "title": Title of the recording
    }
    For additional information about each recording use the
    `get_recording` method. """
    return conn._get_paged_json("api/carnatic/recording")

def get_recording(rmbid):
    """ Get specific information about a recording. 
    Arguments:
      rmbid: A recording mbid
    Returns: mbid, title, artists, raaga, taala, work
             artists includes performance relationships attached
             to the recording, the release, and the release artists.
    """
    return conn._dunya_query_json("api/carnatic/recording/%s" % rmbid)

def get_artists():
    """ Get a list of Carnatic artists in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing artist information.
    {"mbid": Musicbrainz artist id,
     "name": Name of the artist
    }
    For additional information about each artist use the
    `get_artist` method. """
    return conn._get_paged_json("api/carnatic/artist")

def get_artist(ambid):
    """ Get specific information about an artist.
    Arguments:
      ambid: An artist mbid
    Returns: mbid, name, concerts, instruments, recordings
             concerts, instruments and recordings include information
             from recording- and release-level relationships, as
             well as release artists
    """
    return conn._dunya_query_json("api/carnatic/artist/%s" % ambid)

def get_concerts():
    """ Get a list of Carnatic concerts in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing concert information.
    {"mbid": Musicbrainz concert id,
     "title": title of the concert
    }
    For additional information about each concert use the
    `get_concert` method. """
    return conn._get_paged_json("api/carnatic/concert")

def get_concert(cmbid):
    """ Get specific information about a concert. 
    Arguments:
      cmbid: A concert mbid
    Returns: mbid, title, artists, tracks
             artists includes performance relationships attached
             to the recordings, the release, and the release artists.
    """
    return conn._dunya_query_json("api/carnatic/concert/%s" % cmbid)

def get_works():
    """ Get a list of Carnatic works in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing work information.
    {"mbid": Musicbrainz work id,
     "name": work name
    }
    For additional information about each work use the
    `get_work` method. """
    return conn._get_paged_json("api/carnatic/work")

def get_work(wmbid):
    """ Get specific information about a work.
    Arguments:
      wmbid: A work mbid
    Returns: mbid, title, composer, raagas, taalas, recordings
    """
    return conn._dunya_query_json("api/carnatic/work/%s" % wmbid)

def get_raagas():
    """ Get a list of Carnatic raagas in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing raaga information.
    {"id": raaga id,
     "name": name of the raaga
    }
    For additional information about each raaga use the
    `get_raaga` method. """
    return conn._get_paged_json("api/carnatic/raaga")

def get_raaga(rid):
    """ Get specific information about a raaga.
    Arguments:
      rid: A raaga id
    Returns: id, name, artists, works, composers
             artists includes artists with recording- and release-
             level relationships to a recording with this raaga
    """
    return conn._dunya_query_json("api/carnatic/raaga/%s" % str(rid))

def get_taalas():
    """ Get a list of Carnatic taalas in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing taala information.
    {"id": taala id,
     "name": name of the taala
    }
    For additional information about each taala use the
    `get_taala` method. """
    return conn._get_paged_json("api/carnatic/taala")

def get_taala(tid):
    """ Get specific information about a taala.
    Arguments:
      tid: A taala id
    Returns: id, name, artists, works, composers
             artists includes artists with recording- and release-
             level relationships to a recording with this raaga
    """
    return conn._dunya_query_json("api/carnatic/taala/%s" % str(tid))

def get_instruments():
    """ Get a list of Carnatic instruments in the database.
    This function will automatically page through API results.
    Returns: A list of dictionaries containing instrument information.
    {"id": instrument id,
     "name": Name of the instrument
    }
    For additional information about each instrument use the
    `get_instrument` method. """
    return conn._get_paged_json("api/carnatic/instrument")

def get_instrument(iid):
    """ Get specific information about an instrument.
    Arguments:
      iid: An instrument id
    Returns: id, name, artists
             artists includes artists with recording- and release-
             level performance relationships of this instrument.
    """
    return conn._dunya_query_json("api/carnatic/instrument/%s" % str(iid))

def download_mp3(recordingid, location):
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    recording = get_recording(recordingid)
    concert = get_concert(recording["concert"]["mbid"])
    title = recording["title"]
    artists = " and ".join([a["name"] for a in concert["concert_artists"]])
    contents = docserver.get_mp3(recordingid)
    name = "%s - %s.mp3" % (artists, title)
    path = os.path.join(location, name)
    open(path, "wb").write(contents)

def download_concert(concertid, location):
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    concert = get_concert(concert_id)
    artists = " and ".join([a["name"] for a in concert["concert_artists"]])
    concertname = concert["title"]
    concertdir = os.path.join(location, "%s - %s" % (artists, concertname))
    for r in concert["tracks"]:
        rid = r["mbid"]
        title = r["title"]
        contents = docserver.get_mp3(rid)
        name = "%s - %s.mp3" % (artists, title)
        path = os.path.join(concertdir, name)
        open(path, "wb").write(contents)
