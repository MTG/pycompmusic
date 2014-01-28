import requests
import logging
logger = logging.getLogger("dunya")

import conn

def get_recordings(artistid=None, concertid=None, raaga=None, taala=None, instrument=None, work=None):
    return conn._get_paged_json("api/carnatic/recording")

def get_artists(raaga=None, taala=None, instrument=None):
    return conn._get_paged_json("api/carnatic/artist")

def get_concerts():
    return conn._get_paged_json("api/carnatic/concert")

def get_concert(mbid):
    return conn._dunya_query_json("api/carnatic/concert/%s" % mbid)

def get_works():
    return conn._get_paged_json("api/carnatic/work")

def get_raagas():
    return conn._get_paged_json("api/carnatic/raaga")

def get_taalas():
    return conn._get_paged_json("api/carnatic/taala")

def get_instruments():
    return conn._get_paged_json("api/carnatic/instrument")

