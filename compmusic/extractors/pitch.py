# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

import struct

import essentia.standard
import numpy as np
from docserver import util
from scipy.ndimage.filters import gaussian_filter
import io

import compmusic.extractors


class PitchExtract(compmusic.extractors.ExtractorModule):
    _version = "noguessunv"
    _sourcetype = "mp3"
    _slug = "pitch"

    _output = {"pitch": {"extension": "json", "mimetype": "application/json"}}

    def setup(self):
        # Hop size is 44100*4/900 because our smallest view is 4 seconds long
        # and the image is 900px wide. For 8 seconds, we take every 2,
        # 16 seconds, every 4, and 32 seconds every 8 samples.
        self.add_settings(HopSize=196,
                          FrameSize=2048,
                          BinResolution=10,
                          GuessUnvoiced=False,
                          CentsPerBin=1)

    def run(self, musicbrainzid, fname):
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

        # generating time stamps (because its equally hopped)
        TStamps = np.array(range(0, len(pitch))) * np.float(self.settings.HopSize) / sampleRate
        thepitch = np.array([TStamps, pitch]).transpose()

        return {"pitch": thepitch.tolist()}


class NormalisedPitchExtract(compmusic.extractors.ExtractorModule):
    _abstract = True
    _sourcetype = "mp3"

    _output = {"packedpitch": {"extension": "dat", "mimetype": "application/octet-stream"},
               "normalisedpitch": {"extension": "json", "mimetype": "application/json"},
               "normalisedhistogram": {"extension": "json", "mimetype": "application/json"},
               "drawhistogram": {"extension": "json", "mimetype": "application/json"}}

    def get_histogram(self, pitch, nbins, smoothness=1):
        valid_pitch = [p for p in pitch if p > 0]
        bins = [i - 0.5 for i in range(0, nbins + 1)]
        histogram, edges = np.histogram(valid_pitch, bins, density=True)
        smoothed = gaussian_filter(histogram, smoothness)

        return smoothed

    def normalise_pitch(self, pitch, tonic, bins_per_octave, max_value):
        eps = np.finfo(np.float).eps
        normalised_pitch = bins_per_octave * np.log2(2.0 * (pitch + eps) / tonic)
        indexes = np.where(normalised_pitch <= 0)
        normalised_pitch[indexes] = 0
        indexes = np.where(normalised_pitch > max_value)
        normalised_pitch[indexes] = max_value
        return normalised_pitch

    def run(self, musicbrainzid, fname):
        pitch = util.docserver_get_json(musicbrainzid, "pitch", "pitch", version="noguessunv")
        tonic = util.docserver_get_contents(musicbrainzid, self.tonicname, "tonic", version=self.tonicversion)
        tonic = float(tonic)

        nppitch = np.array(pitch)
        bpo = 64  # 256 pixel high image spanning 4 octaves = 64px/octave
        height = 255  # Height of the image
        drawpitch = self.normalise_pitch(nppitch[:, 1], tonic, bpo, height)
        packed_pitch = io.BytesIO()
        for p in drawpitch:
            packed_pitch.write(struct.pack("B", p))
        drawhist = self.get_histogram(drawpitch, 256, 1)

        bpo = 120  # 10 cents per bin (original resolution in melody calculation)
        max_value = bpo * 4  # 4 octaves
        simpitch = self.normalise_pitch(nppitch[:, 1], tonic, bpo, max_value)
        simhist = self.get_histogram(simpitch, max_value, 7)

        return {"packedpitch": packed_pitch.getvalue(),
                "normalisedpitch": drawpitch,
                "drawhistogram": drawhist,
                "normalisedhistogram": simhist}


class HindustaniNormalisedPitchExtract(NormalisedPitchExtract):
    _version = "0.1"
    _slug = "hindustaninormalisedpitch"

    tonicname = "hindustanivotedtonic"
    tonicversion = "0.1"


class CarnaticNormalisedPitchExtract(NormalisedPitchExtract):
    _version = "0.1"
    _slug = "carnaticnormalisedpitch"

    tonicname = "carnaticvotedtonic"
    tonicversion = "0.1"
