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
        data_root = "/home/alastair/code/dunya/annotations"
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
            proclist = ["/srv/dunya/PitchCandExt_O0", "-m", "T", "-t", "V", "-i", wavfname]
            p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
            output = p.communicate()
            tonic = output[0]

        return {"tonic": str(tonic)}
