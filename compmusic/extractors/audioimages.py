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

import collections as coll
import os
import tempfile
import wave

from docserver import util

import compmusic.extractors
import imagelib.wav2png as w2png
import io


class AudioImages(compmusic.extractors.ExtractorModule):
    _version = "0.2"
    _sourcetype = "mp3"
    _slug = "audioimages"

    __depends = "wav"

    _output = {"waveform4": {"extension": "png", "mimetype": "image/png", "parts": True},
               "spectrum4": {"extension": "png", "mimetype": "image/png", "parts": True},
               "waveform8": {"extension": "png", "mimetype": "image/png", "parts": True},
               "spectrum8": {"extension": "png", "mimetype": "image/png", "parts": True},
               "waveform16": {"extension": "png", "mimetype": "image/png", "parts": True},
               "spectrum16": {"extension": "png", "mimetype": "image/png", "parts": True},
               "waveform32": {"extension": "png", "mimetype": "image/png", "parts": True},
               "spectrum32": {"extension": "png", "mimetype": "image/png", "parts": True},
               "smallfull": {"extension": "png", "mimetype": "image/png"}
               }

    _zoom_levels = [4, 8, 16, 32]
    _f_min = None
    _f_max = None
    _fft_size = 31
    _scale_exp = None
    _pallete = None

    def make_mini(self, wavfname):
        smallfulloptions = coll.namedtuple('options', 'image_height fft_size image_width f_min f_max scale_exp pallete')
        smallfulloptions.fft_size = 4096
        smallfulloptions.image_height = 65
        smallfulloptions.image_width = 900
        smallfulloptions.f_min = None
        smallfulloptions.f_max = None
        smallfulloptions.f_max = None
        smallfulloptions.pallete = None
        smallfulloptions.scale_exp = None

        smallfullio = io.BytesIO()
        smallfullio.name = "wav.png"
        # We don't use the spectogram, but need to provide it anyway
        smallfullspecio = io.BytesIO()
        smallfullspecio.name = "spec.png"
        invmfccio = io.BytesIO()
        invmfccio.name = "spec.png"
        w2png.genimages(wavfname, smallfullio, smallfullspecio, invmfccio, smallfulloptions)
        return smallfullio.getvalue()

    def run(self, musicbrainzid, fname):
        baseFname, ext = os.path.splitext(os.path.basename(fname))

        wavfname, created = util.docserver_get_wav_filename(musicbrainzid)

        panelWidth = 900  # pixels
        panelHeight = 255  # pixels
        zoomlevels = self._zoom_levels  # seconds
        options = coll.namedtuple('options', 'image_height fft_size image_width f_min f_max scale_exp pallete')
        options.image_height = panelHeight
        options.fft_size = self._fft_size
        options.f_min = self._f_min
        options.f_max = self._f_max
        options.pallete = self._pallete
        options.scale_exp = self._scale_exp

        ret = {}
        for zoom in zoomlevels:
            # At the beginning of each zoom level we reset the image_width
            # since we are modifying it at the end of the last zoom level
            options.image_width = panelWidth

            wvFile = wave.Wave_read(wavfname)
            framerate = wvFile.getframerate()
            totalframes = wvFile.getnframes()

            # We want this many frames per file at this zoom level.
            framesperimage = framerate * zoom

            wfname = "waveform%s" % zoom
            specname = "spectrum%s" % zoom
            inv_mfcc_name = "inv_mfcc_spectrum%s" % zoom
            wfdata = []
            specdata = []
            inv_mfcc_data = []

            sumframes = 0
            while sumframes < totalframes:
                if sumframes + framesperimage > totalframes:
                    remaining_frames = (totalframes - sumframes)
                    options.image_width = options.image_width * remaining_frames / framesperimage
                else:
                    remaining_frames = framesperimage

                fp, smallname = tempfile.mkstemp(".wav")
                os.close(fp)
                data = wvFile.readframes(remaining_frames)
                wavout = wave.open(smallname, "wb")
                # This will set nframes, but writeframes resets it
                wavout.setparams(wvFile.getparams())
                wavout.writeframes(data)
                wavout.close()
                sumframes += framesperimage

                specio = io.BytesIO()
                # Set the name attr so that PIL gets the filetype hint
                specio.name = "spec.png"
                wavio = io.BytesIO()
                wavio.name = "wav.png"
                in_mfcc_io = io.BytesIO()
                in_mfcc_io.name = "melspec.png"

                w2png.genimages(smallname, wavio, specio, in_mfcc_io, options)
                os.unlink(smallname)

                specdata.append(specio.getvalue())
                wfdata.append(wavio.getvalue())
                inv_mfcc_data.append(in_mfcc_io.getvalue())

            ret[wfname] = wfdata
            ret[specname] = specdata
            ret[inv_mfcc_name] = inv_mfcc_data

        ret["smallfull"] = self.make_mini(wavfname)
        if created:
            os.unlink(wavfname)

        return ret
