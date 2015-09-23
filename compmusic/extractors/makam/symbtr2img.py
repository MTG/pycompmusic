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
import symbtr2xml 
import tempfile
from subprocess import call
import os
from os.path import isfile, join
from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class Symbtr2Png(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "score"
    _output = {
            "score": {"extension": "png", "mimetype": "image/png", "parts": True},
    }


    def run(self, musicbrainzid, fpath):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        fname = symbtr['name']

        finfo = fname.split('/')[-1].split('--')
        finfo[-1] = finfo[-1][:-4]

        makam = finfo[0]
        form = finfo[1]
        usul = finfo[2]
        name = finfo[3]
        try:
            composer = finfo[4]
        except:
            composer = None
        name = name.replace('_', ' ').title()
        composer = composer.replace('_', ' ').title()

        fp, smallname = tempfile.mkstemp(".xml")
        os.close(fp)

        piece = symbtr2xml.symbtrscore(fpath, makam, form, usul, name, composer)
        piece.convertsymbtr2xml(smallname)

        tmp_dir = tempfile.mkdtemp()
        call(["mscore-self", "-platform minimal", smallname, "-b", "-o", "%s/%s.png" % (tmp_dir, musicbrainzid), "-d"])
      
        ret = {'score': []}
        for f in sorted(os.listdir(tmp_dir)):
            if isfile(join(tmp_dir, f)):
                img_file = open(join(tmp_dir, f))
                ret['score'].append(img_file.read())
                img_file.close()
                os.remove(join(tmp_dir, f)) 
        os.rmdir(tmp_dir)
        os.unlink(smallname)
        return ret



