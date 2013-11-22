import compmusic.essentia
import numpy as np
import cStringIO as StringIO
import struct
import sys

import essentia.standard
import intonation

from docserver import util

class PitchExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.4"
    __sourcetype__ = "mp3"
    __slug__ = "pitch"

    __depends__ = "tonic"
    __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}}

    def setup(self):
        # Hop size is 44100*4/900 because our smallest view is 4 seconds long
        # and the image is 900px wide. For 8 seconds, we take every 2,
        # 16 seconds, every 4, and 32 seconds every 8 samples.
        self.add_settings(HopSize=196,
                          FrameSize=2048,
                          BinResolution=10,
                          GuessUnvoiced=True,
                          CentsPerBin=1)


    def run(self, fname):
        audioLoader = essentia.standard.EasyLoader(filename=fname)
        monoLoader = essentia.standard.MonoLoader(filename=fname)
        sampleRate = monoLoader.paramValue("sampleRate")
        equalLoudness = essentia.standard.EqualLoudness(sampleRate=sampleRate)
        audio = equalLoudness(audioLoader())
        self.logger.info('Calculating pitch')
        pitch = essentia.standard.PredominantMelody(hopSize=self.settings.HopSize,
                                    frameSize=self.settings.FrameSize,
                                    binResolution=self.settings.BinResolution,
                                    guessUnvoiced=self.settings.GuessUnvoiced)(audio)

        pitch = pitch[0]
        self.logger.info('done')

        #generating time stamps (because its equally hopped)
        TStamps = np.array(range(0,len(pitch)))*np.float(self.settings.HopSize)/sampleRate
        thepitch = np.array([TStamps, pitch]).transpose()

        return {"pitch": thepitch.tolist()}


class NormalisedPitchExtract(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "normalisedpitch"

    __depends__ = "pitch"

    __output__ = {"packedpitch": {"extension": "dat", "mimetype": "application/octet-stream"},
            "normalisedpitch": {"extension": "json", "mimetype": "application/json"},
            "normalisedhistogram": {"extension": "json", "mimetype": "application/json"},
            "histogram": {"extension": "json", "mimetype": "application/json"}}

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

        recording.histogram.set_smoothness(100)
        #return [recording.histogram.x, recording.histogram.y]

        #This would instead return a raw histogram without smoothing.
        return zip(recording.histogram.x.tolist(), recording.histogram.y.tolist())

    def normalise_pitch(self, pitch):
        eps = np.finfo(np.float).eps
        tonic = util.docserver_get_contents(self.musicbrainz_id, "ctonic", "tonic")
        tonic = float(tonic)
        print "got tonic", tonic
        factor = 1200.0 / self.settings.CentsPerBin
        normalised_pitch = []
        two_to_sixteen = 2**16
        for p in pitch:
            normalised = np.log2(2.0 * (p+eps) / tonic)
            normalised = np.max([normalised, 0])
            factored = np.min([normalised * factor, two_to_sixteen])
            normalised_pitch.append(int(factored))
        return normalised_pitch

    def run(self, fname):
        eps = np.finfo(np.float).eps
        pitch = util.docserver_get_json(self.musicbrainz_id, "pitch", "pitch")
        histogram = util.docserver_get_json(self.musicbrainz_id, "pitch", "histogram")

        histpitch = 1200 * np.log2(pitch + eps)
        hist_in = np.array([TStamps, histpitch]).transpose()
        p_histogram = self.get_histogram(hist_in)

        normalised_pitch = self.normalise_pitch(pitch)
        normalised_pitch = {"normalised": normalised_pitch}

        packed_pitch = StringIO.StringIO()
        #for p in normalised_pitch:
        #    packed_pitch.write(struct.pack("H", p))

        return {"packedpitch": packed_pitch.getvalue(),
                "normalisedpitch": normalised_pitch,
                "normalisedhistogram": p_histogram}
