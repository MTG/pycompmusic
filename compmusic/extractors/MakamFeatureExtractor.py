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

import compmusic.extractors

from essentia import Pool
from essentia.standard import *

from math import ceil
from numpy import size
from numpy import array
from numpy import transpose
from numpy import vstack

class PitchExtractMakam(compmusic.extractors.ExtractorModule):
    __version__ = "0.2"
    __sourcetype__ = "mp3"
    __slug__ = "makampitch"
    __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}}

    def setup(self):
        self.add_settings(hopSize = 128, 
			frameSize = 2048, 
			sampleRate = 44100, 
			guessUnvoiced = True, 
			binResolution = 7.5, 
			peakDistributionThreshold = 2)

    def run(self, fname):
        run_predominant_melody = PredominantMelody(hopSize = self.settings.hopSize, 
						frameSize = self.settings.frameSize, 
						binResolution = self.settings.binResolution,
						guessUnvoiced=self.settings.guessUnvoiced,
						peakDistributionThreshold = self.settings.peakDistributionThreshold)
    
        audio = MonoLoader(filename = fname)()
        audio = EqualLoudness()(audio)
        pitch, pitchConf = run_predominant_melody(audio)

        #generating time stamps (because its equally hopped)
        time_stamps = array(range(0,len(pitch)))*float(self.settings.hopSize)/self.settings.sampleRate
        
        out = transpose(vstack((time_stamps, pitch, pitchConf)))
        #savetxt('test.txt', out, delimiter="\t")
        return {"pitch": out}
