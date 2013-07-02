from log import log
import urllib2
import xml.etree.ElementTree as etree

import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

MUSICBRAINZ_COLLECTION_CARNATIC = ""
MUSICBRAINZ_COLLECTION_HINDUSTANI = ""
MUSICBRAINZ_COLLECTION_MAKAM = ""

def ws_ids(xml):
    ids = []
    tree = etree.fromstring(xml)
    count = int(list(list(tree)[0])[2].attrib["count"])
    for rel in list(list(list(tree)[0])[2]):
        ids.append(rel.attrib["id"])
    return (count, ids)


def get_releases_in_collection(collection):
    """Get a list of the releases in the specified musicbrainz collection"""

    releases = []
    count = 25
    offset = 0
    while offset < count:
        log.debug("offset", offset)
        url = "http://musicbrainz.org/ws/2/collection/%s/releases?offset=%d" % (collection, offset)
        xml = urllib2.urlopen(url).read()
        count, ids = ws_ids(xml)
        releases.extend(ids)
        offset += 25
    return releases

def get_collection_name(collection):
    """ Get the name of a collection """
    url = "http://musicbrainz.org/ws/2/collection/%s/releases" % (collection, )
    xml = urllib2.urlopen(url).read()
    tree = etree.fromstring(xml)
    name = list(list(tree)[0])[0]
    return name.text

def metadata_for_release(releaseid):
    """ Get the title """
