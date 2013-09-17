import compmusic.essentia
import numpy as np

import essentia.standard

class PitchExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "pitch"

    def run(self, fname):
        HopSize = 128
        FrameSize = 2048
        BinResolution = 10
        GuessUnvoiced = True
        output = "Pitch"

        audio = essentia.standard.MonoLoader(filename=fname)()
        pitch = essentia.standard.PredominantMelody(hopSize=HopSize,
                                    frameSize=FrameSize,
                                    binResolution=BinResolution,
                                    guessUnvoiced=GuessUnvoiced)(audio)
        if output == "Pitch":
            pitch = pitch[0]
        else:
            pitch = pitch[1]        
        #generating time stamps (because its equally hopped)
        TStamps = np.array(range(0,len(pitch)))*np.float(HopSize)/44100.0
        dump = np.array([TStamps, pitch]).transpose()
        return dump

class PitchExtract2(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "pitch2"

    def run(self, fname):
        loader = essentia.standard.EasyLoader(filename=fname, sampleRate=44100)
        equalLoudness = essentia.standard.EqualLoudness(sampleRate=44100)
        audio = loader()
        audioDL = equalLoudness(audio)

        pitch = essentia.standard.PitchPolyphonic(binResolution=1)
        res = pitch(audioDL)

        t = np.linspace(0, len(res[0])*128.0/44100, len(res[0]))
        data = zip(t, res[0], res[1])
        data = np.array(data)
        return data
