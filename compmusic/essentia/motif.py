import compmusic.essentia
import numpy as np

import essentia.standard

class MotiveExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "motive"

    def run(self, fname):
        
        audio = essentia.standard.MonoLoader(filename=fname)()
        # sankalp to finish

        return [{"starttime": 0, "endtime": 0, "label": ""}]
