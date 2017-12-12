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
import re
import json
import tempfile

import compmusic.extractors
from tomato.symbolic.scoreconverter import ScoreConverter

from docserver import util
from os.path import isfile, join
from compmusic import dunya
from settings import token
from compmusic.dunya import makam
dunya.set_token(token)

class Symbtr2Png(compmusic.extractors.ExtractorModule):
    _version = "0.2"
    _sourcetype = "symbtrtxt"
    _slug = "score"
    _output = {
            "xmlscore": {"extension": "xml", "mimetype": "application/xml"},
            "score": {"extension": "svg", "mimetype": "image/svg+xml", "parts": True},
    }


    def run(self, musicbrainzid, fpath):
        symbtrmu2 = util.docserver_get_symbtrmu2(musicbrainzid)
        print(symbtrmu2)
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        fname = symbtr['name']
        finfo = fname.split('/')[-1]

        fp, tmpxml = tempfile.mkstemp(".xml")
        os.close(fp)

        tmply = tmpxml.replace(".xml",".ly")
        tmp_dir = tempfile.mkdtemp()

        # parameters
        render_metadata = False  # Don't add the metadata stored in MusicXML to Lilypond 
        # as they're displayed on the left panel in the recording page in Dunya frontend
        svg_paper_size = 'junior-legal'  # The paper size of the svg output pages

        # instantiate analyzer object
        scoreConverter = ScoreConverter()
        


        xml_output, ly_output, svg_output, txt_ly_mapping = scoreConverter.convert(
                    fpath, symbtrmu2, symbtr_name=finfo, mbid=musicbrainzid, 
                    render_metadata=render_metadata, xml_out=tmpxml, ly_out=tmply, 
                    svg_out=tmp_dir, svg_paper_size=svg_paper_size)
        
        ret = {'score': [], 'xmlscore': ''}
        
        musicxml = open(xml_output)
        ret['xmlscore'] = musicxml.read()
        musicxml.close()

        os.unlink(tmpxml)
        os.unlink(tmpxml.replace('.xml','.ly'))

        files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)]
        files = filter(os.path.isfile, files)
        files.sort(key=lambda x: os.path.getmtime(x))

        for f in files:
            if f.endswith('.svg'):
                svg_file = open(f)
                score = svg_file.read()
                ret['score'].append(score)
                svg_file.close()
                os.remove(f)
        os.rmdir(tmp_dir)
        return ret



