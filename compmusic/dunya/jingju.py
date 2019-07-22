import errno
import logging
import os

from requests.exceptions import HTTPError

logger = logging.getLogger("dunya")

from compmusic.dunya import conn
import compmusic.dunya.docserver

COLLECTIONS = None


def set_collections(collections):
    """ Set a list of collections mbid to restrict the queries.
    You must call this before you can make any other calls, otherwise
    they won't be restricted.

    Arguments:
        collections: list of collections mbids

    """
    global COLLECTIONS
    if not isinstance(collections, list):
        raise ValueError('`collections` must be a list')
    COLLECTIONS = collections


def _get_collections():
    extra_headers = None
    if COLLECTIONS:
        extra_headers = {}
        extra_headers['Dunya-Collection'] = ','.join(COLLECTIONS)
    return extra_headers


def get_recordings(recording_detail=False):
    """ Get a list of jingju recordings in the database.
    This function will automatically page through API results.

    :param recording_detail: if True, return full details for each recording like :func:`get_recording`

    returns: A list of dictionaries containing recording information::

        {"mbid": Musicbrainz recording id,
         "title": Title of the recording
        }

    For additional information about each recording use :func:`get_recording`.

    """
    extra_headers = _get_collections()
    args = {}
    if recording_detail:
        args['detail'] = '1'
    return conn._get_paged_json("api/jingju/recording", extra_headers=extra_headers, **args)


def get_recording(rmbid):
    """ Get specific information about a recording.

    :param rmbid: A recording mbid

    :returns: instrumentalists, mbid, performers, release, shengqiangbanshi, title, work.

    """
    extra_headers = _get_collections()
    return conn._dunya_query_json("api/jingju/recording/%s" % rmbid, extra_headers=extra_headers)


def get_artists(artist_detail=False):
    """ Get a list of Jingju artists in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing artist information::

        {"mbid": Musicbrainz artist id,
        "name": Name of the artist}

    For additional information about each artist use :func:`get_artist`

    """

    extra_headers = _get_collections()
    args = {}
    if artist_detail:
        args['detail'] = '1'
    return conn._get_paged_json("api/jingju/artist", extra_headers=extra_headers, **args)


def get_artist(ambid):
    """ Get specific information about an artist.

    :param ambid: An artist mbid

    :returns: alias, instrument, mbid, name, recordings, role_type.

    """
    extra_headers = _get_collections()
    return conn._dunya_query_json("api/jingju/artist/%s" % (ambid), extra_headers=extra_headers)


def get_releases():
    """ Get a list of Jingju releases in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing release information::

        {"mbid": Musicbrainz release id,
         "title": title of the release
        }

    For additional information about each release use :func:`get_release`

    """
    extra_headers = _get_collections()
    return conn._get_paged_json("api/jingju/release", extra_headers=extra_headers)


def get_release(rmbid):
    """ Get specific information about a release.

    :param rmbid: A release mbid
    :returns: artists, mbid, recordings, title.

    """
    extra_headers = _get_collections()
    return conn._dunya_query_json("api/jingju/release/%s" % rmbid, extra_headers=extra_headers)


def get_works():
    """ Get a list of Carnatic works in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing work information::

        {"mbid": Musicbrainz work id,
         "name": work name
        }

    For additional information about each work use :func:`get_work`.

    """
    return conn._get_paged_json("api/jingju/work")


def get_work(wmbid):
    """ Get specific information about a work.

    :param wmbid: A work mbid
    :returns: mbid, play, recordings, score, title.

    """
    return conn._dunya_query_json("api/jingju/work/%s" % (wmbid))


def download_mp3(recordingid, location):
    """Download the mp3 of a document and save it to the specificed directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the mp3 to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    recording = get_recording(recordingid)
    # release = get_release(recording["release"][0]["mbid"])
    title = recording["title"]
    artists = " and ".join([a["name"] for a in recording["performers"]])
    contents = compmusic.dunya.docserver.get_mp3(recordingid)
    name = "%s - %s.mp3" % (artists, title)
    name = name.replace("/", "-")
    path = os.path.join(location, name)
    open(path, "wb").write(contents)
    return name


def download_release(release_id, location):
    """Download the mp3s of all recordings in a release and save
    them to the specificed directory.

    :param release: The MBID of the release
    :param location: Where to save the mp3s to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    release = get_release(release_id)
    # artists = " and ".join([a["name"] for a in concert["concert_artists"]])
    releasename = release["title"]
    releasedir = "%s" % releasename
    releasedir = releasedir.replace("/", "-")
    releasedir = os.path.join(location, releasedir)
    try:
        os.makedirs(releasedir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(releasedir):
            pass
        else:
            raise

    for r in release["recordings"]:
        rid = r["mbid"]
        title = r["title"]
        artists = " and ".join([a["name"] for a in r["performers"]])
        disc = r["disc"]
        disctrack = r["disctrack"]
        contents = compmusic.dunya.docserver.get_mp3(rid)
        name = "%s - %s - %s - %s.mp3" % (disc, disctrack, artists, title)
        path = os.path.join(releasedir, name)
        open(path, "wb").write(contents)

def download_score(externalid, location):
    """Download the score of a document and save it to the specified directory.

    :param externalid: Combination of serieid:workid of a score
    :param location: Where to save the score file to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    try:
        contents = compmusic.dunya.docserver.file_for_document(recordingid, 'musicxmlscore')
        name = "%s.xml" % (recordingid)
        path = os.path.join(location, name)
        with open(path, "wb") as file:
            file.write(contents)
    except HTTPError:
        print("%s score is not stored in Dunya" % recordingid)

