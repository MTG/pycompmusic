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
from tonicidentifier.tonicidentifier import TonicLastNote
from pitchfilter.pitchfilter import PitchPostFilter
from ahenkidentifier import ahenkidentifier
from docserver import util

from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")



class TonicIdentifier(compmusic.extractors.ExtractorModule):
  _version = "0.1"
  _sourcetype = "mp3"
  _slug = "tonicidentifier"
  _output = {
          "tonic": {"extension": "json", "mimetype": "application/json"},
          "ahenk": {"extension": "json", "mimetype": "application/json"},
          "pitch_distribution": {"extension": "json", "mimetype": "application/json"}
          }


  def run(self, musicbrainzid, fname):

      pitch_file = util.docserver_get_filename(musicbrainzid, "initialmakampitch", "pitch", version="0.6")

      pitch = json.load(open(pitch_file, 'r'))

      flt = PitchPostFilter()
      pitch = flt.run(pitch)

      tonic_identifier = TonicLastNote()
      tonic, pitch, pitch_chunks, pitch_distribution, stable_pitches = tonic_identifier.identify(pitch)
      dist_json = {'bins': pitch_distribution.bins.tolist(), 'vals': pitch_distribution.vals.tolist(),
              'kernel_width': pitch_distribution.kernel_width, 'ref_freq': pitch_distribution.ref_freq, 
              'step_size': pitch_distribution.step_size}
      
      
      rec_data = dunya.makam.get_recording(musicbrainzid)

      output = {'tonic': tonic, 'pitch_distribution': dist_json}
      if len(rec_data['makamlist']) != 0:
          makam_data = dunya.makam.get_makam(rec_data['makamlist'][0]['uuid'])
          makam = makam_data['symtr_key']
          
          ahenk = ahenkidentifier.identify(tonic['value'], makam)
          output["ahenk"] = ahenk

      return output

