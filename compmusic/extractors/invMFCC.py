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
# author georgi.dzhambazov@upf.edu

import compmusic.extractors
import numpy as np
from numpy.linalg import inv

import essentia.standard
from numpy import meshgrid, sqrt, cos, pi
from matplotlib.pyplot import imshow


class InvMFCC(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "invMFCC"
    _output = {"invMFCC": {"extension": "json", "mimetype": "application/json"},}

    def setup(self):
        # Hop size is 44100*4/900 because our smallest view is 4 seconds long
        # and the image is 900px wide. For 8 seconds, we take every 2,
        # 16 seconds, every 4, and 32 seconds every 8 samples.
        # Number of Mel filters, Number of COEFS
        self.add_settings(HopSize=196,
                          FrameSize=2048,
                          GuessUnvoiced=False,
                          BANDS = 40,                              
                          COEFS = 13)
        
        ### prepare stage for MFCCs
        self.w = essentia.standard.Windowing(type = 'hann')
        self.spectrum = essentia.standard.Spectrum()
        self.mfcc = essentia.standard.MFCC(numberBands=self.settings.BANDS, numberCoefficients=self.settings.COEFS)
        self.inv_DCT = inv(self.dctmtx(self.settings.BANDS))[:,1:self.settings.COEFS] # The inverse DCT matrix. Change the index to [0:COEFS] if you want to keep the 0-th coefficient
        

    def run(self, musicbrainzid, fname):
        audioLoader = essentia.standard.EasyLoader(filename=fname)
        monoLoader = essentia.standard.MonoLoader(filename=fname)
        
        sampleRate = monoLoader.paramValue("sampleRate")
        equalLoudness = essentia.standard.EqualLoudness(sampleRate=sampleRate)
        audio = equalLoudness(audioLoader())
        

        self.logger.info('Calculating MFCCs...')            
         
        mfccs = []
        for frame in essentia.standard.FrameGenerator(audio, frameSize = self.settings.FrameSize, hopSize = self.settings.HopSize):
            mfcc_bands, mfcc_coeffs = self.frame_to_mfcc(frame) 
            mfccs.append(mfcc_coeffs)
        mfccs = essentia.array(mfccs).T
        
        self.logger.info('Calculating inverse MFCCs...')
        ### inverse DCT computation
        
        inv_mfccs = np.dot(self.inv_DCT, mfccs[1:,:])
        
#         imshow(inv_mfccs, aspect="auto", interpolation="none", origin="lower")
        self.logger.info('done') 

        #generating time stamps (because its equally hopped)
        TStamps = np.array(range(0, inv_mfccs.shape[1])) * np.float(self.settings.HopSize)/sampleRate
        inv_mfccs_and_ts = inv_mfccs.transpose()

        return {"invMFCC": inv_mfccs_and_ts.tolist()}
    
    def frame_to_mfcc(self, frame):
        '''
        Parameters
        ----------
        frame : array of float32 
            frame of audio samples
        
        Returns
        -------
        mfcc : array of float32
            mfcc - array
        
        '''
        mfcc_bands, mfcc_coeffs = self.mfcc(self.spectrum(self.w(frame)))
        
        return mfcc_bands, mfcc_coeffs
        
    def dctmtx(self, n):
        """
        Return the DCT-II matrix of order n as a numpy array.
        taken from  https://github.com/avaitla/HenryVsRudolph/blob/master/Python/MFCC.py
        """
        x,y = meshgrid(range(n), range(n))
        
        D = sqrt(2.0/n) * cos(pi * (2*x+1) * y / (2*n))
        D[0] /= sqrt(2)
        return D

if __name__=='__main__':
    recMBID = '727cff89-392f-4d15-926d-63b2697d7f3f'
    la = InvMFCC()  
    ret = la.run(recMBID, '/home/georgid/workspace/SourceFilterContoursMelody/smstools/sounds/vignesh.wav')
    print ret
    
