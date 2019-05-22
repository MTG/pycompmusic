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

import requests
import compmusic
import os

AUDIO_FILES = "/home/alastair/audio/carnatic"
RELEASE_MAP = {}

def get_coverart_from_directories(directories=[]):
    """Find some coverart in the files that are part of a directory"""
    for d in directories:
        files = [os.path.join(d, f) for f in os.listdir(d)]
        files = [f for f in files if compmusic.is_mp3_file(f)]
        for f in files:
            coverart = compmusic.get_coverart(f)
            if coverart:
                return coverart
    return None

def get_coverart_from_caa(releaseid):
    """Get the cover art inside a file, otherwise try on CAA"""
    url = "https://coverartarchive.org/release/%s/front" % releaseid
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    return None
