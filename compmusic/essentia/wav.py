import compmusic.essentia
import subprocess

class Mp3ToWav(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "wav"

    __output__ = {"wave": {"extension": "wav", "mimetype": "audio/wave"}}

    def run(self, fname):
        proclist = ["lame", "--decode", fname, "-"]
        p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
        audiocontents = p.communicate()[0]

        return {"wave": audiocontents}
