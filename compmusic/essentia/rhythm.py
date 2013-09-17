import compmusic.essentia
import numpy as np

import essentia.standard

class RhythmExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "rhythm"

    def run(self, fname):
        
        audio = essentia.standard.MonoLoader(filename=fname)()
        # ajay to finish

        return {"sections": [{"start": 0, "end": 0, "label": ""}],
                "tatumperiod": 0,
                "timeticks": [1,2,3],
                "tempo": {1: 0, 2:0, 3.4:0}
                }
