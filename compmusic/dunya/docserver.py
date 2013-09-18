import requests
import urlparse
import urllib
import os

DUNYA_ROOT = "localhost:8001"

def _dunya_query(path, **kwargs):
    if not kwargs:
        kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, unicode):
            kwargs[key] = value.encode('utf8')
    url = urlparse.urlunparse((
        'http',
        DUNYA_ROOT,
        'document/%s' % path,
        '',
        urllib.urlencode(kwargs),
        ''
    ))
    g = requests.get(url)
    g.raise_for_status()
    return g

def _dunya_query_json(path, **kwargs):
    """Make a query to dunya and expect the results to be JSON"""
    g = _dunya_query(path, **kwargs)
    return g.json()

def _dunya_query_file(path, **kwargs):
    """Make a query to dunya and return the raw result"""
    g = _dunya_query(path, **kwargs)
    return g.content

def get_collections():
    """Get a list of all collections in the server"""
    path = "collections"
    return _dunya_query_json(path)

def collection(slug):
    """Get the documents (recordings) in a collection.
    Arguments:
      slug: the name of the collection
    """
    path = "%s" % slug
    return _dunya_query_json(path)

def recording(recordingid):
    """Get the details of a single Musicbrainz recording
    Arguments:
      recordingid: Musicbrainz recording ID"""
    path = "by-id/%s" % recordingid
    return _dunya_query_json(path)

def filetypes_for_recording(recordingid):
    """Get the available source filetypes for a Musicbrainz recording
    Arguments:
      recordingid: Musicbrainz recording ID
    Returns:
      a list of filetypes in the database for this recording"""
    path = "by-id/%s" % recordingid
    recording = _dunya_query_json(path)
    return recording["sourcefiles"]

def file_for_recording(recordingid, filetype):
    """Get the contents of a source file, based on the given filetype
    Arguments:
      recordingid: Musicbrainz recording ID
      filetype: the file extension (from filetypes_for_recording)
    Returns:
      the contents of the file requested"""
    path = "by-id/%s/%s" % (recordingid, filetype)
    return _dunya_query_file(path)

def mp3_for_recording(recordingid):
    """Helper method to directly get the mp3 file of a recording
    Arguments:
      recordingid: Musicbrainz recording ID
    Returns:
      the contents of the mp3 file of the given recording"""
    return file_for_recording(recordingid, "mp3")

def derived_filetypes_for_recording(recordingid):
    """Get the available derived filetypes for a Musicbrainz recording
    Arguments:
      recordingid: Musicbrainz recording ID
    Returns:
      The available derived filetypes for this recording, as a dictionary
      of {filetype: [available,versions]}"""
    path = "by-id/%s" % recordingid
    recording = _dunya_query_json(path)
    ret = {}
    for t in recording.get("derivedfiles", []):
        ret[t["extension"]] = t["versions"]
    return ret

def latest_derived_file_for_recording(recordingid, derivedtype):
    """Get the most recent derived file given a filetype
    Arguments:
      recordingid: Musicbrainz recording ID
      derivedtype: the computed filetype (from derived_filetypes_for_recording)
    Returns:
      The contents of the most recent version of the derived file"""
    path = "by-id/%s/%s" % (recordingid, derivedtype)
    return _dunya_query_file(path)

def derived_file_for_recording_version(recordingid, derivedtype, version):
    """Get a specific version of a derived file given a filetype
    Arguments:
      recordingid: Musicbrainz recording ID
      derivedtype: the computed filetype (from derived_filetypes_for_recording)
      version: the version number of the filetype (from derived_filetypes_for_recording)
    Returns:
      The contents of the derived file at the given version"""
    path = "by-id/%s/%s" % (recordingid, derivedtype)
    return _dunya_query_file(path)
    pass
