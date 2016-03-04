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

import os
import re
import json
import tempfile
import socket

import compmusic.extractors
from subprocess import call
from os.path import isfile, join
from makam.musicxml2lilypond import ScoreConverter

class Musicxml2Svg(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrxml"
    _slug = "svgscore"
    _output = {
            "score": {"extension": "svg", "mimetype": "image/svg+xml", "parts": True},
    }


    def run(self, musicbrainzid, fpath):
        temp_name = next(tempfile._get_candidate_names())
        tmpfile = "/tmp/%s.ly" % temp_name

        server_name = socket.gethostname()
        call(["/mnt/compmusic/%s/lilypond/usr/bin/musicxml2ly" % server_name, "--no-page-layout", fpath, "-o", tmpfile])
        
        tmp_dir = tempfile.mkdtemp()
        call(["lilypond", '-dpaper-size=\"junior-legal\"', "-dbackend=svg", "-o" "%s" % (tmp_dir), tmpfile])

        ret = {'score': []}

        os.unlink(tmpfile)
        
        regex = re.compile(r'.*<a style="(.*)" xlink:href="textedit:\/\/\/.*:([0-9]+):([0-9]+):([0-9]+)">.*')
        files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)]
        files = filter(os.path.isfile, files)
        files.sort(key=lambda x: os.path.getmtime(x))

        for f in files:
            if f.endswith('.svg'):
                svg_file = open(f)
                score = svg_file.read()
                ret['score'].append(regex.sub(r'<a style="\1" id="l\2-f\3-t\4" from="\3" to="\4">',score))
                svg_file.close()
                os.remove(f)
        os.rmdir(tmp_dir)
        return ret



