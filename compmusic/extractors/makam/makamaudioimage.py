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

class MakamAudioImage(AudioImages):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "makamaudioimages"
    _depends = "dunyamakampitch"

    _output = {
            "waveform8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "spectrum8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "smallfull": {"extension": "png", "mimetype": "image/png"},
            "pitch": { "extension": "dat", "mimetype": "application/octet-stream"},
            "pitchmax": { "extension": "json", "mimetype": "application/json"}
        }

    _zoom_levels =  [8]
    _fft_size = 4096

    def run(self, musicbrainzid, fname):
        melody = util.docserver_get_filename(musicbrainzid, "dunyamakampitch", "pitch", version="0.1")        
        print melody
        pitch = open(melody,'r')
        pitch = json.loads(pitch.read())
 
        # pitches as bytearray 
        packed_pitch = cStringIO.StringIO() 
        max_pitch = max(pitch) 
        height = 255 
        for p in pitch: 
            packed_pitch.write(struct.pack("B", int(p * 1.0 / max_pitch * height)))
        
        self._f_min = 0.1 
        self._f_max = max(pitch) 
        print self._f_max
        ret = super(MakamAudioImage, self).run(musicbrainzid, fname)
        ret['pitch'] = packed_pitch.getvalue()
        ret['pitchmax'] = {'value': max_pitch}
        return ret
