import compmusic.essentia
import subprocess

import tempfile
import os

class Mp3ToWav(compmusic.essentia.EssentiaModule):
    __version__ = "0.4"
    __sourcetype__ = "mp3"
    __slug__ = "wav"

    __output__ = {"wave": {"extension": "wav", "mimetype": "audio/wave"}}

    def run(self, fname):
        fp, tmpname = tempfile.mkstemp(".wav")
        os.close(fp)
        proclist = ["lame", "--decode", fname, tmpname]
        p = subprocess.Popen(proclist)
        p.communicate()

        contents = open(tmpname, "rb").read()
        os.unlink(tmpname)
        return {"wave": contents}
