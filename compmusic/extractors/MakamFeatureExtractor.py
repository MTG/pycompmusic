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

from pylab import plt

class PitchExtractMakam(compmusic.extractors.ExtractorModule):
	__version__ = "0.1"
	__sourcetype__ = "mp3"
	__slug__ = "pitch"

#    __depends__ = ""
	__output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}}

	def setup(self):
		self.add_settings(hopSize = 128,
                          frameSize = 2048,
                          sampleRate = 44100,
                          guessUnvoiced = True,
                          type = 'hann',
                          minFrequency = 20,
                          maxFrequency = 20000,
                          maxPeaks = 100,
                          magnitudeThreshold = 0,
                          orderBy = "magnitude",
                          peakDistributionThreshold = 1.4)

	def run(self, fname):
		run_windowing = Windowing(type=self.settings.type, zeroPadding = 3 * self.settings.frameSize) # Hann window with x4 zero padding
		run_spectrum = Spectrum(size=self.settings.frameSize * 4)

		run_spectral_peaks = SpectralPeaks(minFrequency=self.settings.minFrequency,
				maxFrequency = self.settings.maxFrequency,
			    maxPeaks = self.settings.maxPeaks,
			    sampleRate = self.settings.sampleRate,
			    magnitudeThreshold = self.settings.magnitudeThreshold,
			    orderBy = self.settings.orderBy)

		run_pitch_salience_function = PitchSalienceFunction()
		run_pitch_salience_function_peaks = PitchSalienceFunctionPeaks()
		run_pitch_contours = PitchContours(hopSize=self.settings.hopSize,
										   peakDistributionThreshold = self.settings.peakDistributionThreshold)

		run_pitch_contours_melody = PitchContoursMelody(guessUnvoiced=self.settings.guessUnvoiced,
														hopSize=self.settings.hopSize)
		pool = Pool();

		# load audio and eqLoudness
		audio = MonoLoader(filename = fname)()
		run_equal_loudness = EqualLoudness()(audio)

		for frame in FrameGenerator(audio,frameSize=self.settings.frameSize, hopSize=self.settings.hopSize):
		    frame = run_windowing(frame)
		    spectrum = run_spectrum(frame)
		    peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)
		    salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
		    salience_peaks_bins, salience_peaks_saliences = run_pitch_salience_function_peaks(salience)
		    if not size(salience_peaks_bins):
			salience_peaks_bins = array([0])
		    if not size(salience_peaks_saliences):
			salience_peaks_saliences = array([0])

		    pool.add('salience', salience)
		    pool.add('allframes_salience_peaks_bins', salience_peaks_bins)
		    pool.add('allframes_salience_peaks_saliences', salience_peaks_saliences)

		# post-processing: contour tracking
		contours_bins, contours_saliences, contours_start_times, duration = run_pitch_contours(
			  pool['allframes_salience_peaks_bins'],
			  pool['allframes_salience_peaks_saliences'])

		sampleRate = 44100
		time_stamps = [float(float(tt*128)/sampleRate) for tt in range(0,len(pool['allframes_salience_peaks_bins']))]

		#---------------cent to Hz conversion---------------------#
		for i in range(0,len(contours_bins)):
			for j in range(0,len(contours_bins[i])):
				hz = 55*(2.**(((10.*(contours_bins[i][j])))/1200))
				contours_bins[i][j] = hz
		#---------------------------------------------------------#

		[pitch, time_stamps] = self.ContourSelection(contours_bins,contours_start_times,duration)

		thepitch = array([time_stamps, pitch]).transpose()

		return {"pitch": thepitch.tolist()}

	def ContourSelection(self,contours_bins,contours_start_times,duration):
		durationTime = duration
		pitchContours = contours_bins
		startTime = contours_start_times
		sampleRate = self.settings.sampleRate

		#duration in samples
		durSample = int(ceil((durationTime * 44100)/128))

		pitch = []
		sampleStartTime =[]
		sampleEndTime = []
		lenContours = []
		lenContoursInd = []

		#-----Lenght of contours and indexes----#
		[lenContours.append(len(i)) for i in pitchContours]

		for i in lenContours:
			lenContoursInd.append(lenContours.index(max(lenContours)))
			lenContours[lenContours.index(max(lenContours))] = 0
		#---------------------------------------#

		######start & end times##################
		endTime = []
		time = []

		hopSize = self.settings.hopSize
		tt = hopSize*(1./44100)

		#end time
		for i in range(0,len(pitchContours)):
			dur = len(pitchContours[i]) * tt
			end = startTime[i] + dur
			endTime.append(end)
		#------------------------------hopSize---------#

		#-------------pitch---------------------#
		pitch = []
		sampleStartTime =[]
		sampleEndTime = []

		#Start points of contours in Samples
		[sampleStartTime.append(int(startTime[i] * 44100./128)-1) for i in range(0,len(startTime))]

		#End points of contours in Samples
		[sampleEndTime.append(int(endTime[i] * 44100./128)-1) for i in range(0,len(endTime))]

		#Longest pitch contour
		pitch = [-1] * (durSample)
		pitch[sampleStartTime[lenContoursInd[0]]:sampleEndTime[lenContoursInd[0]]] = pitchContours[lenContoursInd[0]]

		#----------contour selection-----------#
		for i in range(1, len(pitchContours)):
			ind = lenContoursInd[i]
			temp = pitchContours[ind]
			tempStartTime = sampleStartTime[ind]
			tempEndTime = sampleEndTime[ind]

			for j in range(0,len(temp)):
				if pitch[tempStartTime + j] == -1:
					pitch[tempStartTime + j] = temp[j]
		#--------------------------------------#

		#-----time_stamps----------------------#
		time_stamps = [float(float(tt*128)/sampleRate) for tt in range(0,len(pitch))]

		#-----deleting -1 from pitch array-----#
		zeroIndex = []

		for i in range(0,len(pitch)):
			if pitch[i] == -1:
				zeroIndex.append(i)
		for i in zeroIndex:
			pitch[i] = 0
		#--------------------------------------#
		return pitch, time_stamps
