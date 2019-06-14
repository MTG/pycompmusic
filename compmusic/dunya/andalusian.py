import json
import logging
import os

logger = logging.getLogger("dunya")

import compmusic.dunya.conn
import compmusic.dunya.docserver

COLLECTIONS = None


def set_collections(collections):
    """ Set a list of collections mbid to restrict the queries.
    You must call this before you can make any other calls, otherwise 
    they won't be restricted.

    :param collections: list of collections mbids
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
    """ Get a list of andalusian recordings in the database.
    This function will automatically page through API results.

    :param recording_detail: if True, return full details for each recording 
    like :func:`get_recording`

    :returns: A list of dictionaries containing recording information::
        {"mbid": MusicBrainz recording ID, "title": Title of the recording,
        "transliterated_title"}

    For additional information about each recording use :func:`get_recording`.
    """
    extra_headers = _get_collections()
    args = {}
    if recording_detail:
        args['detail'] = '1'
    return compmusic.dunya.conn._get_paged_json("api/andalusian/recording", 
            extra_headers=extra_headers, **args)


def get_recording(rmbid):
    """ Get specific information about a recording.

    :param rmbid: A recording mbid

    :returns: mbid, title, transliterated_name, musescore_url, archive url and sections.

         ``sections`` include information about the start and end time of the section,
         the name and the transliterated name.
    """
    extra_headers = _get_collections()
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/recording/%s" % rmbid, 
            extra_headers=extra_headers)


def get_artists():
    """ Get a list of Andalusian artists in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing artist information::

        {"mbid": MusicBrainz artist ID, "name": Name of the artist}
    """
    extra_headers = _get_collections()
    return compmusic.dunya.conn._get_paged_json("api/andalusian/artist", 
            extra_headers=extra_headers)


def get_artist(ambid):
    """ Get specific information about an artist.

    :param ambid: An artist mbid

    :returns: mbid, name, releases, instruments, recordings

             ``releases``, ``instruments`` and ``recordings`` include
             information from recording- and release-level
             relationships, as well as release artists
    """
    extra_headers = _get_collections()
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/artist/%s" % ambid, 
            extra_headers=extra_headers)

def get_works():
    """ Get a list of Andalusian works in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing work information::

        {"mbid": MusicBrainz work ID, "name": work name}

    For additional information about each work use :func:`get_work`.
    """
    extra_headers = _get_collections()
    return compmusic.dunya.conn._get_paged_json("api/andalusian/work", 
            extra_headers=extra_headers)

def get_work(wmbid):
    """ Get specific information about a work.

    :param wmbid: A work mbid
    :returns: mbid, title, recordings
    """
    extra_headers = _get_collections()
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/work/%s" % wmbid, 
        extra_headers=extra_headers)


def get_mizans():
    """ Get a list of Andalusian mizan in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing mizan information::

        {uuid, name, transliterated_name, display_order}

    For additional information about each raag use :func:`get_mizan`.
    """
    return compmusic.dunya.conn._get_paged_json("api/andalusian/mizan")

def get_mizan(mid):
    """ Get specific information about a mizan.

    :param rid: A mizan id or uuid
    :returns: uuid, name, transliterated_name, display_order
    """
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/mizan/%s" % str(mid))

def get_tabs():
    """ Get a list of Andalusian in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing tab information::

        {uuid, name, transliterated_name, display_order}

    For additional information about each taal use :func:`get_tab`.
    """
    return compmusic.dunya.conn._get_paged_json("api/andalusian/tab")

def get_tab(tid):
    """ Get specific information about a tab.

    :param tid: A tab id or uuid
    :returns: uuid, name, transliterated_name, display_order
    """
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/tab/%s" % str(tid))

def get_nawbas():
    """ Get a list of Andalusian nawbas in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing nawba information::

        {uuid, name, transliterated_name, display_order}

    For additional information about each nawba use :func:`get_nawba.
    """
    return compmusic.dunya.conn._get_paged_json("api/andalusian/nawba")


def get_nawba(nid):
    """ Get specific information about a nawba.

    :param nid: A nawba id or uuid
    :returns: uuid, name, transliterated_name, display_order
    """
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/nawba/%s" % str(nid))


def get_forms():
    """ Get a list of Andalusian forms in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing form information::

        {"uuid": form uuid, "name": name of the form}

    For additional information about each form use :func:`get_form`
    """
    return compmusic.dunya.conn._get_paged_json("api/andalusian/form")


def get_form(fid):
    """ Get specific information about a form.

    :param fid: A form id or uuid
    :returns: uuid, name, transliterated_name, display_order
    """
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/form/%s" % str(fid))


def get_instruments():
    """ Get a list of Andalusian instruments in the database.
    This function will automatically page through API results.

    :returns: A list of dictionaries containing instrument information::

        {"id": instrument id, "name": Name of the instrument}

    For additional information about each instrument use :func:`get_instrument`
    """
    return compmusic.dunya.conn._get_paged_json("api/andalusian/instrument")


def get_instrument(iid):
    """ Get specific information about an instrument.

    :param iid: An instrument id
    :returns: id, name
    """
    return compmusic.dunya.conn._dunya_query_json("api/andalusian/instrument/%s" % str(iid))


def download_mp3(recordingid, location):
    """Download the mp3 of a document and save it to the specified directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the mp3 to
    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    recording = get_recording(recordingid)
    title = recording["title"]
    contents = compmusic.dunya.docserver.get_mp3(recordingid)
    name = "%s.mp3" % (title)
    name = name.replace("/", "-")
    path = os.path.join(location, name)
    open(path, "wb").write(contents)
    return name

def download_xml(recordingid, location):
    """Download the xml score of a document and save it to the specified directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the xml to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    try:
        contents = compmusic.dunya.docserver.file_for_document(recordingid, 'symbtrxml')
        name = "%s.xml" % (recordingid)
        path = os.path.join(location, name)
        open(path, "wb").write(contents)
    except:
        print("%s score is not stored in Dunya"% recordingid)

def get_works_by_query(amid= '', mid='',tid='', nid='', fid='', iid=''):
    """ Get the works filtered according to the input andalusian artist, mizan, tab,
    nawba, form, instrument and artist.

    :param amid: An artist id or uuid
    :param mid: A mizan id or uuid
    :param tid: A tab id or uuid
    :param nid: An nawba id or uuid
    :param fid: A form id or uuid
    :param fbid: A instrument mbid
    :param ibid: An artist mbid
    :returns: A list of dictionaries containing work/s
    """
    path = 'work?artist={0}&mizan={1}&tab={2}&nawba={3}&form={4}&instrument={5}'
    path = path.format(amid,mid,tid,nid,fid,iid)
    return compmusic.dunya.conn._get_paged_json("api/andalusian/" + path)

def download_pitch_track(recordingid, location):
    """ Download the pitch track from a specific recording and save it to the specified 
    directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the json to
    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)
    try:
        result = compmusic.dunya.docserver.get_document_as_json(recordingid, "andalusianpitch", subtype="pitch_filt")
        name = recordingid + "_pitchtrack.json"
        output = os.path.join(location, name)
        with open(output, 'w') as output:
            json.dump(result, output)
    except:
        print("%s pitch track is not stored in Dunya"% recordingid)


def download_pitch_distribution(recordingid, location):
    """ Download the pitch distribution from a specific recording and save it to the specified directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the json to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)
    try:
        result = compmusic.dunya.docserver.get_document_as_json(recordingid, "andalusianpitch", subtype="pitch_distribution")
        name = recordingid + "_pitchdistribution.json"
        output = os.path.join(location, name)
        with open(output, 'w') as output:
            json.dump(result, output)
    except:
        print("%s pitch distribution is not stored in Dunya"% recordingid)

def download_lyrics(recordingid, location):
    """ Download the arabic and transliteration version of the lyrics of a specific recording
    :param recordingid: The MBID of the recording
    :param location: Where to save the json to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)
    try:
        result = compmusic.dunya.docserver.file_for_document(recordingid, "andalusian-lyrics").decode('utf-8')
        name = recordingid + "_lyrics.json"
        output = os.path.join(location, name)
        with open(output, 'w') as json_file:
            json.dump(result, json_file)
    except:
        print("%s lyrics is not stored in Dunya"% recordingid)