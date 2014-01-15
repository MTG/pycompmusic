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

import compmusic.essentia
import numpy as np

import essentia.standard
import subprocess

import tempfile
import os
from docserver import util
import yaml

class TonicExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "tonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def run(self, fname):

        audio = essentia.standard.MonoLoader(filename=fname)()
        tonic = essentia.standard.TonicIndianArtMusic()(audio)

        return {"tonic": str(tonic)}

class CTonicExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.2"
    __sourcetype__ = "mp3"
    __slug__ = "ctonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def get_from_file(self, mbid):
        data_root = "/mnt/compmusic/incoming/derived/annotations"
        mbidfile = os.path.join(data_root, "%s.yaml" % mbid)
        if os.path.exists(mbidfile):
            ydata = yaml.load(open(mbidfile))
            tonic = ydata.get("tonic", {}).get("votedValue", None)
            return tonic
        return None

    def run(self, fname):

        yamltonic = self.get_from_file(self.musicbrainz_id)
        if yamltonic:
            print "Got tonic from a yaml file"
            tonic = yamltonic
        else:
            print "Need to calculate the tonic from scratch"
            wavfname = util.docserver_get_filename(self.musicbrainz_id, "wav", "wave")
            proclist = ["/srv/dunya/PitchCandExt_O3", "-m", "T", "-t", "V", "-i", wavfname]
            p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
            output = p.communicate()
            tonic = output[0]

        return {"tonic": str(tonic)}
