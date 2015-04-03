# -*- coding: utf-8 -*-
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
# If you are using this extractor please cite the following paper:
#
# Atlı, H. S., Uyar, B., Şentürk, S., Bozkurt, B., and Serra, X. (2014). Audio 
# feature extraction for exploring Turkish makam music. In Proceedings of 3rd 
# International Conference on Audio Technologies for Music and Media, Ankara, 
# Turkey.

import compmusic.extractors

from essentia import Pool
from essentia.standard import *

from math import ceil
from numpy import size
from numpy import array
from numpy import vstack
from numpy import transpose

import json
import scipy.io
import cStringIO

class PitchExtractMakam(compmusic.extractors.ExtractorModule):
  __version__ = "0.5"
  __sourcetype__ = "mp3"
  __slug__ = "makampitch"
  #    __depends__ = ""
  __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"},
                "matlab": {"extension": "mat", "mimetype": "application/octet-stream"},
                "settings": {"extension": "json", "mimetype": "application/json"}
                }

  def setup(self):
    self.add_settings(hopSize = 128,
                      frameSize = 2048,
                      sampleRate = 44100,
                      binResolution = 7.5,
                      guessUnvoiced = True,
                      filterType = 'hann',
                      minFrequency = 20,
                      maxFrequency = 20000,
                      maxPeaks = 100,
                      magnitudeThreshold = 0,
                      peakDistributionThreshold = 1.4)

  def run(self, fname):
    citation = u'Atlı, H. S., Uyar, B., Şentürk, S., Bozkurt, B., and Serra, X. ' \
                '(2014). Audio feature extraction for exploring Turkish makam music. ' \
                'In Proceedings of 3rd International Conference on Audio Technologies ' \
                'for Music and Media, Ankara, Turkey.'

    run_windowing = Windowing(type=self.settings.filterType, zeroPadding = 3 * self.settings.frameSize) # Hann window with x4 zero padding
    run_spectrum = Spectrum(size=self.settings.frameSize * 4)

    run_spectral_peaks = SpectralPeaks(minFrequency=self.settings.minFrequency,
            maxFrequency = self.settings.maxFrequency,
            maxPeaks = self.settings.maxPeaks,
            sampleRate = self.settings.sampleRate,
            magnitudeThreshold = self.settings.magnitudeThreshold,
            orderBy = 'magnitude')

    run_pitch_salience_function = PitchSalienceFunction(binResolution=self.settings.binResolution) # converts unit to cents, 55 Hz is taken as the default reference
    run_pitch_salience_function_peaks = PitchSalienceFunctionPeaks(binResolution=self.settings.binResolution)
    run_pitch_contours = PitchContours(hopSize=self.settings.hopSize,
            binResolution=self.settings.binResolution,
            peakDistributionThreshold = self.settings.peakDistributionThreshold)
    pool = Pool();

    # load audio and eqLoudness
    audio = MonoLoader(filename = fname)() # MonoLoader resamples the audio signal to 44100 Hz by default
    audio = EqualLoudness()(audio)

    for frame in FrameGenerator(audio,frameSize=self.settings.frameSize, hopSize=self.settings.hopSize):
      frame = run_windowing(frame)
      spectrum = run_spectrum(frame)
      peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)
      salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
      salience_peaks_bins, salience_peaks_contourSaliences = run_pitch_salience_function_peaks(salience)
      if not size(salience_peaks_bins):
          salience_peaks_bins = array([0])
      if not size(salience_peaks_contourSaliences):
          salience_peaks_contourSaliences = array([0])

      pool.add('allframes_salience_peaks_bins', salience_peaks_bins)
      pool.add('allframes_salience_peaks_contourSaliences', salience_peaks_contourSaliences)

    # post-processing: contour tracking
    contours_bins, contours_contourSaliences, contours_start_times, duration = run_pitch_contours(
            pool['allframes_salience_peaks_bins'],
            pool['allframes_salience_peaks_contourSaliences'])

    # run the simplified contour selection
    [pitch, pitch_salience] = self.ContourSelection(contours_bins,contours_contourSaliences,contours_start_times,duration)

    # cent to Hz conversion
    pitch = [0. if p == 0 else 55.*(2.**(((self.settings.binResolution*(p)))/1200)) for p in pitch]

    # generate time stamps
    time_stamps = [s*self.settings.hopSize/float(self.settings.sampleRate) for s in xrange(0,len(pitch))]

    # [time pitch salience] matrix
    out = transpose(vstack((time_stamps, pitch, pitch_salience)))
    out = out.tolist()
    
    # settings
    settings = self.settings
    settings.update({'version':self.__version__, 
            'slug':self.__slug__, 
            'source': fname,
            'essentiaVersion': essentia.__version__,
            'pitchUnit': 'Hz',
            'citation': citation})

    # matlab 
    matout = cStringIO.StringIO()
    matob = {'pitch': out}
    matob.update(settings)

    scipy.io.savemat(matout, matob)

    return {'pitch': json.dumps(out),
            'matlab': matout.getvalue(),
            'settings': json.dumps(settings)}

  def ContourSelection(self,pitchContours,contourSaliences,startTimes,duration):
    sampleRate = self.settings.sampleRate

    hopSize = self.settings.hopSize

    # number in samples in the audio
    numSamples = int(ceil((duration * sampleRate)/hopSize))

    #Start points of the contours in samples
    startSamples = [int(round(startTimes[i] * sampleRate/float(hopSize))) for i in xrange(0,len(startTimes))]

    pitchContours_noOverlap = []
    startSamples_noOverlap = []
    contourSaliences_noOverlap = []
    lens_noOverlap = []
    while pitchContours: # terminate when all the contours are checked
      #print len(pitchContours)

      # get the lengths of the pitchContours
      lens = [len(k) for k in pitchContours]

      # find the longest pitch contour
      long_idx = lens.index(max(lens))

      # pop the lists related to the longest pitchContour and append it to the new list
      pitchContours_noOverlap.append(pitchContours.pop(long_idx))
      contourSaliences_noOverlap.append(contourSaliences.pop(long_idx))
      startSamples_noOverlap.append(startSamples.pop(long_idx))
      lens_noOverlap.append(lens.pop(long_idx))

      # accumulate the filled samples
      acc_idx = range(startSamples_noOverlap[-1], startSamples_noOverlap[-1] + lens_noOverlap[-1])

      # remove overlaps
      [startSamples, pitchContours, contourSaliences] = self.RemoveOverlaps(startSamples, pitchContours, contourSaliences, lens, acc_idx)
      

    # accumulate pitch and salience
    pitch = array([0.] * (numSamples))
    salience = array([0.] * (numSamples))
    for i in xrange(0,len(pitchContours_noOverlap)):
      startSample = startSamples_noOverlap[i]
      endSample = startSamples_noOverlap[i] + len(pitchContours_noOverlap[i])

      pitch[startSample:endSample] = pitchContours_noOverlap[i]
      salience[startSample:endSample] = contourSaliences_noOverlap[i]

    return pitch, salience.tolist()

  def RemoveOverlaps(self, startSamples, pitchContours, contourSaliences, lens, acc_idx):
    # remove overlaps
    rmv_idx = []
    for i in xrange(0, len(startSamples)):
      #print '_' + str(i)
      # create the sample index vector for the checked pitch contour
      curr_samp_idx = range(startSamples[i], startSamples[i] + lens[i])

      # get the non-overlapping samples
      curr_samp_idx_noOverlap = (list(set(curr_samp_idx) - set(acc_idx)))

      if curr_samp_idx_noOverlap:
        temp = min(curr_samp_idx_noOverlap)
        keep_idx = range(temp-startSamples[i], (max(curr_samp_idx_noOverlap)-startSamples[i])+1)

        # remove all overlapping values
        pitchContours[i] = array(pitchContours[i])[keep_idx]
        contourSaliences[i] = array(contourSaliences[i])[keep_idx]
        # update the startSample
        startSamples[i] = temp
      else: # totally overlapping
        rmv_idx.append(i)

    # remove totally overlapping pitch contours
    rmv_idx = sorted(rmv_idx, reverse=True)
    for r in rmv_idx:
      pitchContours.pop(r)
      contourSaliences.pop(r)
      startSamples.pop(r)

    return startSamples, pitchContours, contourSaliences
