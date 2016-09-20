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
import cStringIO
from compmusic.extractors.audioimages import AudioImages
from docserver import util
import struct
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
from seyiranalyzer import audioseyiranalyzer


class MakamAudioImage(AudioImages):
    _version = "0.3"
    _sourcetype = "mp3"
    _slug = "makamaudioimages"

    _output = {
            "waveform8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "spectrum8": {"extension": "png", "mimetype": "image/png", "parts": True},
            "smallfull": {"extension": "png", "mimetype": "image/png"},
        }

    _zoom_levels =  [8]
    _fft_size = 4096
    _scale_exp = 2
    _pallete = 2

    def run(self, musicbrainzid, fname):
        max_pitch = util.docserver_get_filename(musicbrainzid, "tomatodunya", "pitchmax", version="0.1")
        pitch = json.load(open(max_pitch))

        self._f_min = pitch['min']
        self._f_max = pitch['max']
        ret = super(MakamAudioImage, self).run(musicbrainzid, fname)

        try:
            pitchfile = util.docserver_get_filename(musicbrainzid, "jointanalysis", "pitch", version="0.1")
            loaded_pitch = json.load(open(pitchfile, 'r'))
            # If pitch extraction from jointanalysis failed then load it from audioanlysis
            if not loaded_pitch:
              pitchfile = util.docserver_get_filename(musicbrainzid, "audioanalysis", "pitch", version="0.1")
              loaded_pitch = json.load(open(pitchfile, 'r'))
        except util.NoFileException:
            pitchfile = util.docserver_get_filename(musicbrainzid, "audioanalysis", "pitch", version="0.1")
            loaded_pitch = json.load(open(pitchfile, 'r'))

        pitch = np.array(loaded_pitch['pitch'])

        audioSeyirAnalyzer = audioseyiranalyzer.AudioSeyirAnalyzer()

        # compute number of frames from some simple rules set by the user
        duration = pitch[-1][0]
        min_num_frames = 40
        max_frame_dur = 30
        frame_dur = duration/min_num_frames if duration/min_num_frames<=max_frame_dur else max_frame_dur
        frame_dur = int(5 * round(float(frame_dur)/5))  # round to 5 seconds
        if not frame_dur:
            frame_dur = 5

        seyir_features = audioSeyirAnalyzer.analyze(pitch, frame_dur = frame_dur, hop_ratio = 0.5)

        fimage = tempfile.NamedTemporaryFile(mode='w+', suffix=".png")
        plot(seyir_features, fimage.name)
        fimage.flush()
        fileContent = None
        with open(fimage.name, mode='rb') as file:
            file_content = file.read()
        if not file_content:
            raise Exception("No image generated")
        ret['smallfull'] = file_content

        return ret

def plot(seyir_features, file_location, plot_average_pitch=True, plot_stable_pitches=True,
             plot_distribution=False):

    fig = plt.figure(frameon=False)
    if plot_distribution:
        time_starts = [sf['time_interval'][0] for sf in seyir_features]
        min_time = min(np.diff(time_starts))
        for sf in seyir_features:
            # plot the distributions through time
            yy = sf['pitch_distribution'].bins
            tt = sf['time_interval'][0] + sf['pitch_distribution'].vals * min_time*2
            plt.plot(tt, yy)

    for sf in seyir_features:
        if len(sf['stable_pitches']):
            t_st = sf['time_interval'][0]
            max_peak = max([sp['value'] for sp in sf['stable_pitches']])
            for sp in sf['stable_pitches']:
                clr = 'r' if sp['value'] == max_peak else 'b'
                # map the values from 0-1 to 1-6
                marker_thickness = sp['value']*5+1 
                plt.plot(t_st, sp['frequency'], 'o', color = clr, ms=marker_thickness)

            
    if plot_average_pitch:
        tt = [sf['time_interval'][0] for sf in seyir_features]
        pp = [sf['average_pitch'] for sf in seyir_features]

        plt.plot(tt, pp, color='k', linewidth=3)

    fig.set_size_inches(31.25, 2.6)
    fig.set_tight_layout(True)
    plt.axis('off')
    plt.margins(0,0)

    plt.savefig(file_location, bbox_inches='tight', pad_inches=0) 
