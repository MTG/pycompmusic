import numpy as np
import imagelib.wav2png as w2png
import logging
import collections as coll
import wave 
import os

class AudioImages():#(compmusic.essentia.EssentiaModule):
    __version__ = "0.1"
    __sourcetype__ = "wav"
    __slug__ = "audioimages"

    def run(self, fname):
        baseFname, ext = os.path.splitext(os.path.basename(fname))
        print baseFname
        print ext
        if ext != ".wav":
            print "Cannot work on non-wav files. Please convert it before input"
        panelWidth = 900		              # pixels
        panelHeight = 255		              # pixels
        zoomlevels = [4, 8, 16, 32]           	      # seconds
        options = coll.namedtuple('options', 'image_height fft_size image_width')
        options.image_height = 255
        options.fft_size = 4096
        baseSpecName = baseFname + "_spectrogram"
        baseWavName = baseFname + "_waveform"
        wvFile = wave.Wave_read(fname)
        wvFileLen = wvFile.getnframes()/(float(wvFile.getframerate()))  # in seconds
        
        for zoom in zoomlevels:
            specname = baseSpecName + "_" + str(zoom) + ".jpg"
            wavname = baseWavName + "_" + str(zoom) + ".png"
            options.image_width = int(round(panelWidth*wvFileLen/float(zoom)))
            w2png.genimages(fname,wavname,specname,options)
            
