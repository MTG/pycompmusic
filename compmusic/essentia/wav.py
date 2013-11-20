import compmusic.essentia
import subprocess

import tempfile
import os
import wave

class Mp3ToWav(compmusic.essentia.EssentiaModule):
    __version__ = "0.5"
    __sourcetype__ = "mp3"
    __slug__ = "wav"

    __output__ = {"wave": {"extension": "wav", "mimetype": "audio/wave"},
                  "length": {"extension": "dat", "mimetype": "text/plain"}
                 }

    def run(self, fname):
        fp, tmpname = tempfile.mkstemp(".wav")
        os.close(fp)
        proclist = ["lame", "--decode", fname, tmpname]
        p = subprocess.Popen(proclist)
        p.communicate()

        wfile = wave.open(tmpname, "rb")
        length = wfile.getnframes() * 1.0 / wfile.getframerate()
        wfile.close()
        contents = open(tmpname, "rb").read()
        os.unlink(tmpname)
        return {"wave": contents, "length": str(int(length))}
