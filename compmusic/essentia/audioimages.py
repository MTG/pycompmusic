import compmusic.essentia
import numpy as np
import imagelib.wav2png as w2png
import logging
import collections as coll
import wave 
import os
import tempfile

from cStringIO import StringIO

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
                  "fullsmall": {"extension": "png", "mimetype": "image/png"}
                 }

    def run(self, fname):
        baseFname, ext = os.path.splitext(os.path.basename(fname))
        print baseFname
        print ext
        
        wavfname = util.docserver_get_filename(self.document_id, "wav", "wave")

        panelWidth = 900		              # pixels
        panelHeight = 255		              # pixels
        zoomlevels = [4, 8, 16, 32]           	      # seconds
        options = coll.namedtuple('options', 'image_height fft_size image_width')
        options.image_height = 255
        options.fft_size = 4096
        baseSpecName = baseFname + "_spectrogram"
        baseWavName = baseFname + "_waveform"
        wvFile = wave.Wave_read(wavfname)
        wvFileLen = wvFile.getnframes()/(float(wvFile.getframerate()))  # in seconds

        ret = {}
        
        for zoom in zoomlevels:
            fp, smallname = tempfile.mkstemp(".wav")
            os.close(fp)

            wfname = "waveform%s" % zoom
            specname = "spectrum%s" % zoom

            specio = StringIO()
            # Set the name attr so that PIL gets the filetype hint
            specio.name = "spec.jpg"
            wavio = StringIO()
            wavio.name = "wav.png"
            
            specname = baseSpecName + "_" + str(zoom) + ".jpg"
            wavname = baseWavName + "_" + str(zoom) + ".png"
            options.image_width = int(round(panelWidth*wvFileLen/float(zoom)))
            w2png.genimages(fname, wavio, specio, options)

            ret[wfname] = wavio.getvalue()
            ret[specname] = specio.getvalue()

            

        return ret
            
