# -*- coding: utf-8 -*-
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
#
# If you are using this extractor please cite the following paper:
#
# Atlı, H. S., Uyar, B., Şentürk, S., Bozkurt, B., and Serra, X. (2014). Audio
# feature extraction for exploring Turkish makam music. In Proceedings of 3rd
# International Conference on Audio Technologies for Music and Media, Ankara,
# Turkey.

import compmusic.extractors.makam.pitch
from docserver import util

from alignedpitchfilter import alignedpitchfilter
import matplotlib.pyplot as plt

from essentia import __version__ as essentia_version
from essentia import Pool
from essentia import array as e_array
import essentia.standard as estd

from math import ceil
from numpy import size
from numpy import array
from numpy import vstack
from numpy import transpose

import os
import struct
import json
import scipy.io
import cStringIO

class DunyaPitchMakam(compmusic.extractors.makam.pitch.PitchExtractMakam):
  _version = "0.1"
  _sourcetype = "mp3"
  _slug = "dunyamakampitch"
  _output = {
          "pitch": {"extension": "json", "mimetype": "application/json"},
          "pitch_corrected":{"extension": "json", "mimetype": "application/json"}
  }

  def setup(self):
    self.add_settings(hopSize = 196, # default hopSize of PredominantMelody
                      frameSize = 2048, # default frameSize of PredominantMelody
                      sampleRate = 44100,
                      binResolution = 7.5, # ~1/3 Hc; recommended for makams
                      minFrequency = 55, # default minimum of PitchSalienceFunction
                      maxFrequency = 1760, # default maximum of PitchSalienceFunction
                      magnitudeThreshold = 0, # default of SpectralPeaks; 0 dB?
                      peakDistributionThreshold = 1.4, # default in PitchContours is 0.9; we need higher in makams
                      filterPitch = True, # call PitchFilter
                      confidenceThreshold = 36, # default confidenceThreshold for pitchFilter
                      minChunkSize = 50) # number of minimum allowed samples of a chunk in PitchFilter; ~145 ms with 128 sample hopSize & 44100 Fs

  def run(self, musicbrainzid, fname):
    output = super(DunyaPitchMakam, self).run(musicbrainzid, fname)
    
    # Compute the pitch octave correction

    tonicfile = util.docserver_get_filename(musicbrainzid, "tonictempotuning", "tonic", version="0.1")
    alignednotefile = util.docserver_get_filename(musicbrainzid, "scorealign", "notesalign", version="0.1")

    print output["pitch"][0]
    pitch = array(output["pitch"])
    
    tonic = json.load(open(tonicfile, 'r'))['scoreInformed']['Value']
    notes = json.load(open(alignednotefile, 'r'))['notes']

    pitch_corrected, synth_pitch, notes = alignedpitchfilter.correctOctaveErrors(pitch, notes, tonic)
    output["pitch_corrected"] = pitch_corrected
    del output["matlab"]
    del output["settings"]
    return output
