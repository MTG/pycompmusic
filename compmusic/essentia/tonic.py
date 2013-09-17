import compmusic.essentia
import numpy as np

import essentia.standard

class TonicExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "tonic"

    def run(self, fname):
        
        audio = essentia.standard.MonoLoader(filename=fname)()
        tonic = essentia.standard.TonicIndianArtMusic()(audio)

        return {"tonic": tonic}
