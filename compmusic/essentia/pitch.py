import compmusic.essentia
import numpy as np
import cStringIO as StringIO
import struct

import essentia.standard

from compmusic.dunya import docserver

class PitchExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "pitch"

    __depends__ = "tonic"
    __output__ = {"pitch": None, "packedpitch": None, "histogram": None}

    def normalise_pitch(self, pitch):
        eps = np.finfo(np.float).eps
        #tonic = docserver.latest_derived_file_for_recording(self.document_id, "tonic")
        tonic = 100
        factor = 1200.0 / self.settings.CentsPerBin
        normalised_pitch = []
        two_to_sixteen = 2**16
        for p in pitch:
            normalised = np.log2(2.0 * (p+eps) / tonic)
            normalised = np.max([normalised, 0])
            factored = np.min([normalised * factor, two_to_sixteen])
            normalised_pitch.append(int(factored))
        return normalised_pitch

    def setup(self):
        self.add_settings(HopSize=128,
                          FrameSize=2048,
                          BinResolution=10,
                          GuessUnvoiced=True,
                          CentsPerBin=1)

    def run(self, fname):
        audioLoader = essentia.standard.EasyLoader(filename=fname, startTime=30, endTime=35)
        monoLoader = essentia.standard.MonoLoader(filename=fname)
        sampleRate = monoLoader.paramValue("sampleRate")
        equalLoudness = essentia.standard.EqualLoudness(sampleRate=sampleRate)
        audio = equalLoudness(audioLoader())
        pitch = essentia.standard.PredominantMelody(hopSize=self.settings.HopSize,
                                    frameSize=self.settings.FrameSize,
                                    binResolution=self.settings.BinResolution,
                                    guessUnvoiced=self.settings.GuessUnvoiced)(audio)

        pitch = pitch[0]

        #generating time stamps (because its equally hopped)
        TStamps = np.array(range(0,len(pitch)))*np.float(self.settings.HopSize)/sampleRate
        dump = np.array([TStamps, pitch]).transpose()

        normalised_pitch = self.normalise_pitch(pitch)

        #p_histogram = get_histogram(normalised_pitch)
        p_histogram = 1

        packed_pitch = StringIO.StringIO()
        for p in normalised_pitch:
            packed_pitch.write(struct.pack("H", p))

        return {"pitch": dump.tolist(),
                "packedpitch": packed_pitch.getvalue(),
                "histogram": p_histogram}

class PitchExtract2(compmusic.essentia.EssentiaModule):
    __version__ = "0.3"
    __sourcetype__ = "mp3"
    __slug__ = "pitch2"

    def run(self, fname):
        self.logger.info("PitchExtract2 logger info")
        return {"woo": "datav3"}
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
