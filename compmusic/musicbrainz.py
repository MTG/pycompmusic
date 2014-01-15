# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
# 
# This file is part of Dunya
# 
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

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
