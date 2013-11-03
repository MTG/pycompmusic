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
    __version__ = "0.1"
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

    def run(self, fname):
        baseFname, ext = os.path.splitext(os.path.basename(fname))
        print baseFname
        print ext

        wavfname, created = util.docserver_get_wav_filename(self.musicbrainz_id)

        panelWidth = 900		              # pixels
        panelHeight = 255		              # pixels
        zoomlevels = [4, 8, 16, 32]           	      # seconds
        zoomlevels = [32]           	      # seconds
        options = coll.namedtuple('options', 'image_height fft_size image_width')
        smallfulloptions = coll.namedtuple('options', 'image_height fft_size image_width')
        options.image_height = panelHeight
        options.image_width = panelWidth
        options.fft_size = 4096
        smallfulloptions.fft_size = 4096
        smallfulloptions.image_height = 65
        wvFile = wave.Wave_read(wavfname)
        framerate = wvFile.getframerate()

        ret = {}

        for zoom in zoomlevels:
            # TODO: Need to reset the file pointer each time around

            # We want this many frames per file at this zoom level.
            # TODO: Will we run out of memory?
            framesperimage = framerate * zoom

            wfname = "waveform%s" % zoom
            specname = "spectrum%s" % zoom
            wfdata = []
            specdata = []

            minidata = []
            # When we make the small image, we generate the parts so that
            # their size will add up to `panelWidth` pixels wide
            totalframes = wvFile.getnframes()
            numsmallparts = math.ceil(totalframes*1.0/framesperimage)
            smallpartsize = int(panelWidth / numsmallparts)
            smallfulloptions.image_width = smallpartsize
            smallfullimage = None
            print "going to make %s parts, each %s in size" % (numsmallparts, smallpartsize)

            sum = 0
            while sum <= totalframes:
                # TODO: The last time around this loop, we need to
                # work out if the imagewidth needs to be smaller
                fp, smallname = tempfile.mkstemp(".wav")
                os.close(fp)
                data = wvFile.readframes(framesperimage)
                wavout = wave.open(smallname, "wb")
                # This will set nframes, but writeframes resets it
                wavout.setparams(wvFile.getparams())
                wavout.writeframes(data)
                wavout.close()
                sum += framesperimage

                specio = StringIO()
                # Set the name attr so that PIL gets the filetype hint
                specio.name = "spec.png"
                wavio = StringIO()
                wavio.name = "wav.png"

                w2png.genimages(smallname, wavio, specio, options)

                if not smallfullimage:
                    smallfullio = StringIO()
                    smallfullio.name = "wav.png"
                    # We don't use this
                    smallfullspecio = StringIO()
                    smallfullspecio.name = "spec.png"
                    w2png.genimages(smallname, smallfullio, smallfullspecio, smallfulloptions)
                    minidata.append(smallfullio.getvalue())

                os.unlink(smallname)

                specdata.append(specio.getvalue())
                wfdata.append(wavio.getvalue())

            if not smallfullimage:
                smallfullimage = Image.new("RGB", (900, 65), (0,0,0))
                # we need to stitch together the parts of the mini image
                for i, data in enumerate(minidata):
                    coord = (smallpartsize*i, 0, smallpartsize*i+smallpartsize, 65)
                    pastedimage = Image.open(StringIO(data))
                    smallfullimage.paste(pastedimage, coord)

                smallfullio = StringIO()
                smallfullimage.save(smallfullio, "png")
                ret["smallfull"] = smallfullio.getvalue()

            ret[wfname] = wfdata
            ret[specname] = specdata

        if created:
            os.unlink(wavefname)

        return ret

