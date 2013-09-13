import requests
import os

DUNYA_ROOT = "http://localhost:8001"

def _dunya_query_json(path):
    #TODO Use http path joining
    path = "%s/document%s" % (DUNYA_ROOT, path)
    g = requests.get(path)
    return g.json

def _dunya_query_file(path):
    path = "%s/document%s" % (DUNYA_ROOT, path)
    g = requests.get(path)
    return g.contents

def collection(slug):
    path = "/%s" % slug
    return _dunya_query_json(path)

def recording(recordingid):
    path = "/by-id/%s" % recordingid
    return _dunya_query_json(path)

def filetypes_for_recording(recordingid):
    path = "/by-id/%s" % recordingid
    recording = _dunya_query_json(path)
    return recording["sourcefiles"]

def file_for_recording(recordingid, filetype):
    path = "/by-id/%s/%s" % (recordingid, filetype)
    return _dunya_query_file(path)

def mp3_for_recording(recordingid):
    path = "/by-id/%s/mp3" % (recordingid, )
    return _dunya_query_file(path)

def derived_filetypes_for_recording(recordingid):
    pass

def latest_derived_file_for_recording(recordingid, derivedtype):
    pass

def derived_file_for_recording_version(recordingid, derivedtype, version):
    pass
