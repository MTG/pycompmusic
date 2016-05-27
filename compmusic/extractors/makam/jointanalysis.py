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
import struct
import json
import scipy.io
import cStringIO
import warnings
import numpy as np

import compmusic.extractors.makam.pitch
from tomato.audio.audioanalyzer import AudioAnalyzer
from tomato.joint.jointanalyzer import JointAnalyzer
from seyiranalyzer.audioseyiranalyzer import AudioSeyirAnalyzer
from docserver import util

from compmusic import dunya
from compmusic.dunya import makam
from settings import token
dunya.set_token(token)


class JointAnalysis(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "jointanalysis"
    _output = {
          "works_intervals": {"extension": "json", "mimetype": "application/json"},
          "tonic": {"extension": "json", "mimetype": "application/json"},
          "pitch": {"extension": "json", "mimetype": "application/json"},
          "melodic_progression": {"extension": "json", "mimetype": "application/json"},
          "tempo": {"extension": "json", "mimetype": "application/json"},
          "pitch_distribution": {"extension": "json", "mimetype": "application/json"},
          "pitch_class_distribution": {"extension": "json", "mimetype": "application/json"},
          "transposition": {"extension": "json", "mimetype": "application/json"},
          "makam": {"extension": "json", "mimetype": "application/json"},
          "note_models": {"extension": "json", "mimetype": "application/json"},
          "notes": {"extension": "json", "mimetype": "application/json"},
          "sections": {"extension": "json", "mimetype": "application/json"},
    }

    def run(self, musicbrainzid, fname):
        output = {
                "works_intervals": {},
               "tonic": {},
                "pitch":{}, 
                "melodic_progression": {}, 
                "tempo": {}, 
                "pitch_distribution": {}, 
                "pitch_class_distribution": {}, 
                "transposition": {}, 
                "makam": {}, 
                "note_models": {}, 
                "notes": {}, 
                "sections": {}
                }

        audioAnalyzer = AudioAnalyzer(verbose=True)
        jointAnalyzer = JointAnalyzer(verbose=True)

        # predominant melody extraction
        pitchfile = util.docserver_get_filename(musicbrainzid, "audioanalysis", "pitch", version="0.1")
        audio_pitch = json.load(open(pitchfile))

        output['pitch'] = audio_pitch
        rec_data = dunya.makam.get_recording(musicbrainzid)
        for w in rec_data['works']:
            symbtr_file = util.docserver_get_symbtrtxt(w['mbid'])
            print symbtr_file
            score_features_file = util.docserver_get_filename(w['mbid'], "scoreanalysis", "metadata", version="0.1")
            score_features = json.load(open(score_features_file))
            joint_features, features = jointAnalyzer.analyze(
                        symbtr_file, score_features, fname, audio_pitch)

            # redo some steps in audio analysis
            features = audioAnalyzer.analyze(
                        metadata=False, pitch=False, **features)

            # get a summary of the analysis
            summarized_features = jointAnalyzer.summarize(
                        score_features=score_features, joint_features=joint_features, 
                            score_informed_audio_features=features)
            audio_pitch = summarized_features['audio'].get('pitch', None)
        
            pitch = summarized_features['audio'].get('pitch', None)
            if pitch:
                pitch['pitch'] = pitch['pitch'].tolist()
            melodic_progression = features.get('melodic_progression', None)
            tonic = features.get('tonic', None)
            tempo = features.get('tempo', None)
            pitch_distribution = features.get('pitch_distribution', None)
            pitch_class_distribution = features.get('pitch_class_distribution', None)
            transposition = features.get('transposition', None)
            makam = features.get('makam', None)
            note_models = features.get('note_models', None)
            notes = summarized_features['joint'].get('notes', None)
            sections = summarized_features['joint'].get('sections', None)

            min_interval = 9999
            max_interval = 0
            for i in notes:
                if i['interval'][0] < min_interval:
                    min_interval = i['interval'][0]
                if i['interval'][1] > max_interval:
                    max_interval = i['interval'][1]

            if pitch_distribution:
                pitch_distribution = pitch_distribution.to_dict()
            if pitch_class_distribution:
                pitch_class_distribution = pitch_class_distribution.to_dict()
            if note_models:
               note_models = to_dict(note_models)
            if melodic_progression:
                AudioSeyirAnalyzer.serialize(melodic_progression)
            output["works_intervals"][w['mbid']] = {"from": min_interval, "to": max_interval}
            output["pitch"] = pitch
            output["melodic_progression"][w['mbid']] = melodic_progression
            output["tonic"][w['mbid']] = tonic
            output["tempo"][w['mbid']] = tempo
            output["pitch_distribution"][w['mbid']] = pitch_distribution
            output["pitch_class_distribution"][w['mbid']] = pitch_class_distribution
            output["transposition"][w['mbid']] = transposition
            output["makam"][w['mbid']] = makam
            output["note_models"][w['mbid']] = note_models
            output["notes"][w['mbid']] = notes
            output["sections"][w['mbid']] = sections


        return output

def to_dict(note_models):
    ret = {}
    for key in note_models.keys():
        distribution = note_models[key]['distribution'].to_dict()
        ret[key] = note_models[key]
        if np.isnan(note_models[key]['performed_interval']['value']):
            ret[key]['performed_interval']['value'] = None
        ret[key]['distribution'] = distribution
        notes = []
        for note in note_models[key]['notes']:
            pitch = note['PitchTrajectory'].tolist()
            notes.append(pitch)
        ret[key]['notes'] = notes
    return ret

class TomatoDunyaMakam(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "tomatodunya"
    _output = {
          "pitch": {"extension": "dat", "mimetype": "application/octet-stream"},
          "pitchmax": { "extension": "json", "mimetype": "application/json"},
    }
    def run(self, musicbrainzid, fname):

        audioAnalyzer = AudioAnalyzer(verbose=True)
        jointAnalyzer = JointAnalyzer(verbose=True)

        audioAnalyzer.set_pitch_extractor_params(hop_size=196, bin_resolution=7.5)
        # predominant melody extraction
        audio_pitch = audioAnalyzer.extract_pitch(fname)

        notes = {}
        rec_data = dunya.makam.get_recording(musicbrainzid)
        for w in rec_data['works']:
            symbtr_file = util.docserver_get_symbtrtxt(w['mbid'])
            print symbtr_file
            score_features_file = util.docserver_get_filename(w['mbid'], "scoreanalysis", "metadata", version="0.1")
            score_features = json.load(open(score_features_file))
            joint_features, features = jointAnalyzer.analyze(
                        symbtr_file, score_features, fname, audio_pitch)

            # redo some steps in audio analysis
            features = audioAnalyzer.analyze(
                        metadata=False, pitch=False, **features)

            # get a summary of the analysis
            summarized_features = jointAnalyzer.summarize(
                        score_features=score_features, joint_features=joint_features, 
                            score_informed_audio_features=features)
            audio_pitch = summarized_features['audio'].get('pitch', None)
        
            #pitch = summarized_features['audio'].get('pitch', None)
            #if pitch:
            #    pitch['pitch'] = pitch['pitch'].tolist()           

            notes[w['mbid']] = summarized_features['joint'].get('notes', None)
        

        pitch = [p[1] for p in audio_pitch['pitch'].tolist()]

        # pitches as bytearray
        packed_pitch = cStringIO.StringIO()
        max_pitch = max(pitch)
        temp = [p for p in pitch if p>0]
        min_pitch = min(temp)

        height = 255
        for p in pitch:
            if p < min_pitch:
                packed_pitch.write(struct.pack("B", 0))
            else:
                packed_pitch.write(struct.pack("B", int((p - min_pitch) * 1.0 / (max_pitch - min_pitch) * height)))

        output = {}
        output['pitch'] = packed_pitch.getvalue()
        output['pitchmax'] = {'max': max_pitch, 'min': min_pitch}

        return output
