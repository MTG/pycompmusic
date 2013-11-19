import compmusic.essentia
import numpy as np
import imagelib.wav2png as w2png
import logging
import collections as coll
import wave
import os
import tempfile
from PIL import Image
import math

from StringIO import StringIO

from docserver import util

class AudioImages(compmusic.essentia.EssentiaModule):
    __version__ = "0.2"
    __sourcetype__ = "mp3"
    __slug__ = "audioimages"

    __depends__ = "wav"

    __output__ = {"waveform4": {"extension": "png", "mimetype": "image/png"},
                  "spectrum4": {"extension": "png", "mimetype": "image/png"},
                "waveform8": {"extension": "png", "mimetype": "image/png"},
                  "spectrum8": {"extension": "png", "mimetype": "image/png"},
                "waveform16": {"extension": "png", "mimetype": "image/png"},
                  "spectrum16": {"extension": "png", "mimetype": "image/png"},
                "waveform32": {"extension": "png", "mimetype": "image/png"},
                  "spectrum32": {"extension": "png", "mimetype": "image/png"},
                  "smallfull": {"extension": "png", "mimetype": "image/png"}
                 }

    def make_mini(self, wavfname):
        smallfulloptions = coll.namedtuple('options', 'image_height fft_size image_width')
        smallfulloptions.fft_size = 4096
        smallfulloptions.image_height = 65
        smallfulloptions.image_width = 900

        smallfullio = StringIO()
        smallfullio.name = "wav.png"
        # We don't use the spectogram, but need to provide it anyway
        smallfullspecio = StringIO()
        smallfullspecio.name = "spec.png"
        w2png.genimages(wavfname, smallfullio, smallfullspecio, smallfulloptions)
        return smallfullio.getvalue()

    def run(self, fname):
        baseFname, ext = os.path.splitext(os.path.basename(fname))

        wavfname, created = util.docserver_get_wav_filename(self.musicbrainz_id)

        panelWidth = 900		              # pixels
        panelHeight = 255		              # pixels
        zoomlevels = [4, 8, 16, 32]           	      # seconds
        options = coll.namedtuple('options', 'image_height fft_size image_width')
        options.image_height = panelHeight
        options.image_width = panelWidth
        options.fft_size = 31

        ret = {}
        for zoom in zoomlevels:
            wvFile = wave.Wave_read(wavfname)
            framerate = wvFile.getframerate()
            totalframes = wvFile.getnframes()

            # We want this many frames per file at this zoom level.
            framesperimage = framerate * zoom

            wfname = "waveform%s" % zoom
            specname = "spectrum%s" % zoom
            wfdata = []
            specdata = []

            sumframes = 0
            while sumframes <= totalframes:
                fp, smallname = tempfile.mkstemp(".wav")
                os.close(fp)
                data = wvFile.readframes(framesperimage)
                wavout = wave.open(smallname, "wb")
                # This will set nframes, but writeframes resets it
                wavout.setparams(wvFile.getparams())
                wavout.writeframes(data)
                wavout.close()
                sumframes += framesperimage

                specio = StringIO()
                # Set the name attr so that PIL gets the filetype hint
                specio.name = "spec.png"
                wavio = StringIO()
                wavio.name = "wav.png"

                w2png.genimages(smallname, wavio, specio, options)
                os.unlink(smallname)

                specdata.append(specio.getvalue())
                wfdata.append(wavio.getvalue())

            ret[wfname] = wfdata
            ret[specname] = specdata

        ret["smallfull"] = self.make_mini(wavfname)
        if created:
            os.unlink(wavfname)

        return ret

