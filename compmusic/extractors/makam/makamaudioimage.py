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
import json
import cStringIO
from compmusic.extractors.audioimages import AudioImages
from docserver import util
import struct
import numpy as np
from scipy.ndimage.filters import gaussian_filter

class MakamAudioImage(AudioImages):
    _version = "0.2"
    _sourcetype = "mp3"
    _slug = "makamaudioimages"
    _depends = "dunyapitchmakam"

    _output = {
            "waveform8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "spectrum8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "smallfull": {"extension": "png", "mimetype": "image/png"},
        }

    _zoom_levels =  [8]
    _fft_size = 4096
    _scale_exp = 2
    _pallete = 2

    def run(self, musicbrainzid, fname):
        max_pitch = util.docserver_get_filename(musicbrainzid, "dunyapitchmakam", "pitchmax", version="0.2")        
        pitch = json.load(open(max_pitch))

        self._f_min = pitch['min']
        self._f_max = pitch['max'] 
        ret = super(MakamAudioImage, self).run(musicbrainzid, fname)
        return ret
