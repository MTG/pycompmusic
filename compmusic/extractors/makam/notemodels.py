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

import os
import compmusic.extractors

import json

from pitchfilter.pitchfilter import PitchPostFilter
from tonicidentifier.tonicidentifier import TonicLastNote
from note_model.NoteModel import NoteModel
from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class NoteModels(compmusic.extractors.ExtractorModule):
  _version = "0.1"
  _sourcetype = "mp3"
  _slug = "notemodels"
  _output = {
          "stable_notes": {"extension": "json", "mimetype": "application/json"},
          }


  def run(self, musicbrainzid, fname):
      
      rec_data = dunya.makam.get_recording(musicbrainzid)

      if len(rec_data['makamlist']) == 0:
          raise Exception('No makam on recording %s' % musicbrainzid)

      makam_data = dunya.makam.get_makam(rec_data['makamlist'][0]['uuid'])
      rec_makam = makam_data['symtr_key']
      
      tonic_file = util.docserver_get_filename(musicbrainzid, "tonicidentifier", "tonic", version="0.1")
      pitch_dist_file = util.docserver_get_filename(musicbrainzid, "tonicidentifier", "pitch_distribution", version="0.1")

      tonic = json.load(open(tonic_file, 'r'))['value']
      pitch_dist = json.load(open(pitch_dist_file, 'r'))
     
      model = NoteModel()
      stable_notes = model.calculate_notes(pitch_dist, tonic, rec_makam)
      return {'stable_notes': stable_notes}

