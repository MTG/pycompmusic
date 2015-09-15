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

import compmusic.extractors
import numpy as np

import essentia.standard
import subprocess

import tempfile
import os
import yaml

class CbrMp3(compmusic.extractors.ExtractorModule):
    """ Convert an mp3 file to a constant bitrate if needed """
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "cbrmp3"

    _output = {"mp3": {"extension": "mp3", "mimetype": "audio/mpeg"}}

    def run(self, fname):
        f = eyed3.load(fname)
        vbr, brate = f.info.bit_rate
        #if vbr or brate > 128:
        # TODO: Could also downgrade all high bitrate audio to 128k
        if vbr:
            fp, tmpname = tempfile.mkstemp(".mp3")
            proclist = ["lame", "-b", "128", fname, tmpname]
            p = subprocess.Popen(proclist)
            p.communicate()

            mp3file = open(tmpname, "rb").read()
            return {"mp3": mp3file}

        # If the file is the cbr, return nothing
        return {}
