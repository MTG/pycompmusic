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
from tonic_identifier.tonic_identifier import TonicLastNote
from pitchfilter.pitchfilter import PitchPostFilter
from docserver import util


class TonicIdentifier(compmusic.extractors.ExtractorModule):
  _version = "0.1"
  _sourcetype = "mp3"
  _slug = "tonicidentifier"
  _output = {"tonic": {"extension": "json", "mimetype": "application/json"},
                "pitch": {"extension": "json", "mimetype": "application/json"},
                "pitch_chunks": {"extension": "json", "mimetype": "application/json"},
                "histo": {"extension": "json", "mimetype": "application/json"},
                }


  def run(self, musicbrainzid, fname):

      pitch_file = util.docserver_get_filename(musicbrainzid, "initialmakampitch", "pitch", version="0.6")

      pitch = json.load(open(pitch_file, 'r'))

      flt = PitchPostFilter()
      pitch = flt.run(pitch)

      tonic_identifier = TonicLastNote()
      tonic, pitch, pitch_chunks, histo = tonic_identifier.identify(pitch)

      histo_out = zip(histo.x.tolist(),histo.y.tolist())
      return {'tonic': tonic,
            'pitch': pitch,
            'pitch_chunks': pitch_chunks,
            'histo': histo_out}

