import compmusic.essentia
import numpy as np
import cStringIO as StringIO
import struct

import essentia.standard
import intonation

from compmusic.dunya import docserver

class PitchExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "pitch"

    __depends__ = "tonic"
    __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}, "packedpitch": None, "histogram": None}

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
        # Hop size is 44100*4/900 because our smallest view is 4 seconds long
        # and the image is 900px wide
        self.add_settings(HopSize=196,
                          FrameSize=2048,
                          BinResolution=10,
                          GuessUnvoiced=True,
                          CentsPerBin=1)

    def get_histogram(self, pitch):
        """
        Given a numpy array of nx2, where the first column is 
        of timestamps, and the second column of pitch values
        normalized to tonic, this function returns a (unsmoothed)
        histogram.
        """
        pitch_obj = intonation.Pitch(pitch[:, 0], pitch[:, 1])
        recording = intonation.Recording(pitch_obj)

        #if no bins are given, the resolution would be 1 cent/bin
        recording.compute_hist(weight="duration") 

        #Uncomment the following couple of lines to return a smooth histogram.
        #The argument refers to standard deviation of gaussian kernel 
        #used for smoothing.

        #recording.histogram.set_smoothness(7)
        #return [recording.histogram.x, recording.histogram.y]

        #This would instead return a raw histogram without smoothing.
        return [recording.histogram.x, recording.histogram.y_raw]

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
    __version__ = "0.6"
    __sourcetype__ = "mp3"
    __slug__ = "pitch2"

    __output__ = {"data1": {"extension": "json", "mimetype": "application/json"},
                  "data2": {"extension": "json", "mimetype": "application/json"},
                 }

    def run(self, fname):
        self.logger.info("PitchExtract2 logger info")

        return {"data1": {"woo": "datav4 part"}, "data2": [{"mything": "pitch-data2part1"}, {"mything": "pitch-data2part2"}]}
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
