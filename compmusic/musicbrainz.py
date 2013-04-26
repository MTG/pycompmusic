import musicbrainzngs

MUSICBRAINZ_COLLECTION_CARNATIC = ""
MUSICBRAINZ_COLLECTION_HINDUSTANI = ""
MUSICBRAINZ_COLLECTION_MAKAM = ""

def ws_ids(xml):
    ids = []
    tree = etree.fromstring(xml)
    for rel in tree.getchildren()[0].getchildren()[2].getchildren():
        ids.append(rel.attrib["id"])
    return ids


def get_releases_in_collection(collection):
    """Get a list of the releases in the specified musicbrainz collection"""

    releases = []
    count = 25
    offset = 0
    while offset < count
        print off
        url = "http://musicbrainz.org/ws/2/collection/5bfb724f-7e74-45fe-9beb-3e3bdb1a119e/releases?offset=%d" % off
        xml = urllib2.urlopen(url).read()
        coll_ids.extend(ws_ids(xml))
        off += 25
