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

import os
import warnings
import json
import compmusic.extractors
import numpy as np
from tomato.audio.audioanalyzer import AudioAnalyzer
from seyiranalyzer.audioseyiranalyzer import AudioSeyirAnalyzer

class AudioAnalysis(compmusic.extractors.ExtractorModule):
  _version = "0.1"
  _sourcetype = "mp3"
  _slug = "audioanalysis"
  _output = {
                "metadata": {"extension": "json", "mimetype": "application/json"},
                "pitch": {"extension": "json", "mimetype": "application/json"},
                "pitch_filtered": {"extension": "json", "mimetype": "application/json"},
                "melodic_progression": {"extension": "json", "mimetype": "application/json"},
                "tonic": {"extension": "json", "mimetype": "application/json"},
                "pitch_distribution": {"extension": "json", "mimetype": "application/json"},
                "pitch_class_distribution": {"extension": "json", "mimetype": "application/json"},
                "transposition": {"extension": "json", "mimetype": "application/json"},
                "note_models": {"extension": "json", "mimetype": "application/json"},
                "makam": {"extension": "json", "mimetype": "application/json"},
                }

  def run(self, musicbrainzid, fname):
    audioAnalyzer = AudioAnalyzer(verbose=True)

    # NOTE: This will take several minutes depending on the performance of your machine
    features = audioAnalyzer.analyze(fname)

    metadata = features.get('metadata', None)
    pitch = features.get('pitch', None)
    pitch_filtered = features.get('pitch_filtered', None)
    melodic_progression = features.get('melodic_progression', None)
    tonic = features.get('tonic', None)
    pitch_distribution = features.get('pitch_distribution', None)
    pitch_class_distribution = features.get('pitch_class_distribution', None)
    transposition = features.get('transposition', None)
    note_models = features.get('note_models', None)
    makam = features.get('makam', None)

    for i in self._output.keys():
        if i not in features:
            warnings.warn("The output %s is missing from the audio analysis" % i)
    if set(features.keys()) != set(self._output.keys()):
        warnings.warn("Output mismatch on audio analysis %s" % features.keys())
    if pitch_distribution:
        pitch_distribution = pitch_distribution.to_dict()
    if pitch_class_distribution:
        pitch_class_distribution = pitch_class_distribution.to_dict()
    if note_models:
        note_models = to_dict(note_models)
    if melodic_progression:
        AudioSeyirAnalyzer.serialize(melodic_progression)
    return {"metadata": metadata, "pitch": pitch, "pitch_filtered": pitch_filtered,
            "melodic_progression": melodic_progression, "tonic": tonic,
            "pitch_distribution": pitch_distribution,
            "pitch_class_distribution": pitch_class_distribution,
            "transposition": transposition, "note_models": note_models, "makam": makam }
def to_dict(note_models):
    ret = {}
    for key in note_models.keys():
        ret[key] = note_models[key]
        if 'distribution' in note_models[key]:
            distribution = note_models[key]['distribution'].to_dict()
            ret[key]['distribution'] = distribution
        if np.isnan(note_models[key]['performed_interval']['value']):
            ret[key]['performed_interval']['value'] = None
        notes = []
        if 'notes' in note_models[key]:
            for note in note_models[key]['notes']:
                if 'PitchTrajectory' in note:
                    pitch = note['PitchTrajectory'].tolist()
                    notes.append(pitch)
        ret[key]['notes'] = notes
    return ret
