import compmusic.essentia
import numpy as np

import essentia.standard
import subprocess

import tempfile
import os
from docserver import util

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
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "ctonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def run(self, fname):
        wavfname = util.docserver_get_filename(self.musicbrainz_id, "wav", "wave")
        proclist = ["/srv/dunya/PitchCandExt_O0", "-m", "T", "-t", "V", "-i", wavfname]
        p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
        output = p.communicate()
        tonic = output[0]

        return {"tonic": str(tonic)}
