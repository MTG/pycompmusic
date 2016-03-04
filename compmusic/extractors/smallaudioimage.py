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
from docserver import util
from compmusic.extractors.audioimages import AudioImages


class SmallAudioImage(AudioImages):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "smallaudioimages"
    _f_min =  None
    _f_max = None
    _fft_size = 31
    _scale_exp = None
    _pallete = None


    _output = {
            "smallfull": {"extension": "png", "mimetype": "image/png"},
        }

    def run(self, musicbrainzid, fname):

        wavfname, created = util.docserver_get_wav_filename(musicbrainzid)
        ret["smallfull"] = self.make_mini(wavfname)
        if created:
            os.unlink(wavfname)

        return ret

